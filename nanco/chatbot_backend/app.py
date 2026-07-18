from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv
import tempfile
import uuid
from functools import wraps
from supabase import create_client, Client
import bcrypt

load_dotenv()

app = Flask(__name__)
# Enable CORS so our frontend can communicate with the backend
CORS(app)

# Initialize Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SECRET_KEY")
supabase: Client = None
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "super-secret-nanco-token")

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or token != f"Bearer {ADMIN_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Initialize Groq client. Make sure GROQ_API_KEY is set in your environment or .env file!
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are Nanco AI, a helpful assistant for Nanco Paints (an ISO 9001-2015 certified company in Malappuram, Kerala). ONLY answer questions related to painting, paint products, and our services. Keep answers VERY short and concise.
You have access to several website tools and sections. When the user asks about a topic, you MUST suggest the relevant tool using exactly this format: [TOOL:Name|image_file|url].
Here is the exact syntax for each section you can suggest:
- Paint prices, costs, or estimating: [TOOL:Paint Calculator|assets/paint calculator.jpg|calculators.html] and [TOOL:Products|assets/products.jpg|products.html]
- Seeing how paint looks in a room: [TOOL:Virtual Paint Visualizer|assets/paint visualizer.jpg|paint_visualizer.html]
- Finding colors and inspiration: [TOOL:Color Studio|assets/colors.jpg|services.html]
- Downloading catalogs: [TOOL:Catalogs|assets/catelog.jpg|services.html]
- Info for paint workers/contractors: [TOOL:Worker Portal|assets/Paint Workers Portal.jpg|login/login.php]
- Finding nearby shops/outlets: [TOOL:Factory Outlets|assets/outlet.png|index.html]
- General services we offer: [TOOL:All Services|assets/house-bg1.png|services.html]
- Knowing more about Nanco: [TOOL:About Us|assets/sa.png|about_us.html]
Always include these [TOOL:...] tags in your response when applicable! DO NOT wrap them in markdown code blocks."""

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])  # list of {role, content}
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        # Build messages list: system prompt + history + current message
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (excluding the last user message since we add it below)
        for msg in history[:-1]:  # exclude last since it's the current user message
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({"role": role, "content": content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
        )
        response_text = chat_completion.choices[0].message.content
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/voice', methods=['POST'])
def voice():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    
    try:
        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name

        # Transcribe using Groq Whisper API
        with open(temp_audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_audio_path, file.read()),
                model="whisper-large-v3",
                response_format="json",
                language="en"
            )
            
        # Clean up temp file
        os.remove(temp_audio_path)
        
        user_text = transcription.text
        
        # Forward the transcribed text to the LLM
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            model="llama-3.1-8b-instant",
        )
        response_text = chat_completion.choices[0].message.content
        
        return jsonify({
            'transcription': user_text,
            'response': response_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# --- SUPABASE ENDPOINTS ---

@app.route('/api/data', methods=['GET'])
def get_data():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        products_data = []
        try:
            products = supabase.table('products').select('*').order('created_at', desc=True).execute()
            products_data = products.data
        except Exception as e:
            print("Error fetching products:", e)

        images_data = []
        try:
            images = supabase.table('gallery_images').select('*').order('created_at', desc=True).execute()
            images_data = images.data
        except Exception as e:
            print("Error fetching gallery_images:", e)

        hero_data = []
        try:
            hero = supabase.table('hero_backgrounds').select('*').order('created_at', desc=True).execute()
            hero_data = hero.data
        except Exception as e:
            print("Error fetching hero_backgrounds:", e)

        return jsonify({
            "products": products_data,
            "images": images_data,
            "heroBgs": hero_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/items', methods=['GET'])
def get_items():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('items').select('*').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/item-categories', methods=['GET'])
def get_item_categories():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('item_categories').select('*').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/icons', methods=['GET'])
def get_icons():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('icons').select('*').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/datasheets', methods=['GET'])
def get_datasheets():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        item_id = request.args.get('item_id')
        query = supabase.table('datasheets').select('*')
        
        # Handle the format eq.TARGET_ID if sent by frontend
        if item_id and item_id.startswith('eq.'):
            actual_id = item_id[3:]
            query = query.eq('item_id', actual_id)
            
        res = query.execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coy-items', methods=['GET'])
def get_coy_items():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('coy_items').select('*').order('created_at', desc=False).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coy-items', methods=['POST'])
@require_auth
def add_coy_item():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        product_id = request.form.get('product_id')
        title = request.form.get('title')
        description = request.form.get('description')
        top_image = request.files.get('top_image')
        bottom_image = request.files.get('bottom_image')

        if not all([product_id, title, description, top_image, bottom_image]):
            return jsonify({"error": "Missing required fields"}), 400

        def upload_image(file_obj, prefix):
            filename = f"coy_{prefix}_{uuid.uuid4().hex}_{file_obj.filename}"
            file_content = file_obj.read()
            file_obj.seek(0)
            storage_path = f"coy_items/{filename}"
            supabase.storage.from_('product-media').upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": file_obj.content_type}
            )
            return supabase.storage.from_('product-media').get_public_url(storage_path)

        top_image_url = upload_image(top_image, "top")
        bottom_image_url = upload_image(bottom_image, "bottom")

        res = supabase.table('coy_items').insert({
            'product_id': product_id,
            'title': title,
            'description': description,
            'top_image_url': top_image_url,
            'bottom_image_url': bottom_image_url
        }).execute()
        
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coy-items/<item_id>', methods=['PUT'])
@require_auth
def update_coy_item(item_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        product_id = request.form.get('product_id')
        title = request.form.get('title')
        description = request.form.get('description')
        top_image = request.files.get('top_image')
        bottom_image = request.files.get('bottom_image')

        if not all([product_id, title, description]):
            return jsonify({"error": "Missing required fields"}), 400

        # Fetch existing item to get old image URLs if we need to replace them
        res = supabase.table('coy_items').select('*').eq('id', item_id).execute()
        if not res.data:
            return jsonify({"error": "Item not found"}), 404
        existing_item = res.data[0]

        update_data = {
            'product_id': product_id,
            'title': title,
            'description': description
        }

        def upload_image(file_obj, prefix):
            filename = f"coy_{prefix}_{uuid.uuid4().hex}_{file_obj.filename}"
            file_content = file_obj.read()
            file_obj.seek(0)
            storage_path = f"coy_items/{filename}"
            supabase.storage.from_('product-media').upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": file_obj.content_type}
            )
            return supabase.storage.from_('product-media').get_public_url(storage_path)

        def delete_old_image(url):
            if url and 'product-media/' in url:
                import urllib.parse
                try:
                    path = url.split('product-media/')[-1]
                    unquoted_path = urllib.parse.unquote(path)
                    res = supabase.storage.from_('product-media').remove([unquoted_path])
                    if isinstance(res, dict) and res.get('error'):
                        # If unquoted fails, try quoted
                        supabase.storage.from_('product-media').remove([path])
                except Exception as e:
                    print("Warning: failed to delete old image:", e)

        if top_image:
            update_data['top_image_url'] = upload_image(top_image, "top")
            delete_old_image(existing_item.get('top_image_url'))
            
        if bottom_image:
            update_data['bottom_image_url'] = upload_image(bottom_image, "bottom")
            delete_old_image(existing_item.get('bottom_image_url'))

        res = supabase.table('coy_items').update(update_data).eq('id', item_id).execute()
        
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coy-items/<item_id>', methods=['DELETE'])
@require_auth
def delete_coy_item(item_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        # Fetch the item first to get image URLs
        res = supabase.table('coy_items').select('*').eq('id', item_id).execute()
        if not res.data:
            return jsonify({"error": "Item not found"}), 404
        
        item = res.data[0]
        paths_to_remove = []
        
        # Extract storage paths from URLs
        import urllib.parse
        for url_key in ['top_image_url', 'bottom_image_url']:
            url = item.get(url_key)
            if url and 'product-media/' in url:
                path = url.split('product-media/')[-1]
                path = urllib.parse.unquote(path)
                paths_to_remove.append(path)
        
        # Delete images from storage
        if paths_to_remove:
            try:
                res = supabase.storage.from_('product-media').remove(paths_to_remove)
                if isinstance(res, dict) and res.get('error'):
                    print("Warning: failed to delete some images:", res)
            except Exception as e:
                print("Warning: failed to delete images during item removal:", e)
            
        # Delete record from database
        supabase.table('coy_items').delete().eq('id', item_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coy-page-details/<coy_id>', methods=['GET'])
def get_coy_page_details(coy_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('coy_page_details').select('*').eq('coy_id', coy_id).execute()
        if not res.data:
            return jsonify({"coy_id": coy_id, "page_data": {}})
        return jsonify(res.data[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coy-page-details/<coy_id>', methods=['POST'])
@require_auth
def save_coy_page_details(coy_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        import json
        page_data_str = request.form.get('page_data')
        if not page_data_str:
            return jsonify({"error": "Missing page_data"}), 400
            
        page_data = json.loads(page_data_str)
        
        def upload_image(file_obj, prefix):
            filename = f"coy_page_{prefix}_{uuid.uuid4().hex}_{file_obj.filename}"
            file_content = file_obj.read()
            file_obj.seek(0)
            storage_path = f"coy_items/{filename}"
            supabase.storage.from_('product-media').upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": file_obj.content_type}
            )
            return supabase.storage.from_('product-media').get_public_url(storage_path)

        if 'features' in page_data:
            for idx, feature in enumerate(page_data['features']):
                file_key = f'feature_img_{idx}'
                if file_key in request.files:
                    img_url = upload_image(request.files[file_key], f"feat_{idx}")
                    feature['img_url'] = img_url

        if 'application' in page_data:
            for idx, phase in enumerate(page_data['application']):
                file_key = f'phase_img_{idx}'
                if file_key in request.files:
                    img_url = upload_image(request.files[file_key], f"phase_{idx}")
                    phase['img_url'] = img_url

        res = supabase.table('coy_page_details').upsert({
            'coy_id': coy_id,
            'page_data': page_data
        }).execute()
        
        return jsonify(res.data[0])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    file = request.files.get('image') or request.files.get('video') or request.files.get('file')
    if not file: return jsonify({"error": "No file provided"}), 400
    file_ext = file.filename.split('.')[-1]
    file_name = f"{uuid.uuid4().hex}.{file_ext}"
    
    try:
        file_bytes = file.read()
        supabase.storage.from_('nanco-assets').upload(file_name, file_bytes, {"content-type": file.content_type})
        public_url = supabase.storage.from_('nanco-assets').get_public_url(file_name)
        return jsonify({"publicUrl": public_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['POST'])
@require_auth
def add_product():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('products').insert(request.json).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:item_id>', methods=['DELETE'])
@require_auth
def delete_product(item_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        # Fetch product to delete its image from storage
        res = supabase.table('products').select('image_url').eq('id', item_id).execute()
        if res.data and len(res.data) > 0 and res.data[0].get('image_url'):
            url = res.data[0]['image_url']
            if 'nanco-assets/' in url:
                file_name = url.split('nanco-assets/')[-1]
                if file_name:
                    supabase.storage.from_('nanco-assets').remove([file_name])
        
        supabase.table('products').delete().eq('id', item_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images', methods=['POST'])
@require_auth
def add_image():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('gallery_images').insert(request.json).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<int:item_id>', methods=['DELETE'])
@require_auth
def delete_image(item_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        # Fetch image to delete from storage
        res = supabase.table('gallery_images').select('url').eq('id', item_id).execute()
        if res.data and len(res.data) > 0 and res.data[0].get('url'):
            url = res.data[0]['url']
            if 'nanco-assets/' in url:
                file_name = url.split('nanco-assets/')[-1]
                if file_name:
                    supabase.storage.from_('nanco-assets').remove([file_name])

        supabase.table('gallery_images').delete().eq('id', item_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hero', methods=['POST'])
@require_auth
def add_hero():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        try:
            res = supabase.table('hero_backgrounds').insert(data).execute()
            return jsonify(res.data)
        except Exception as insert_err:
            safe_data = {k: v for k, v in data.items() if not k.endswith('_color')}
            res = supabase.table('hero_backgrounds').insert(safe_data).execute()
            return jsonify(res.data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/hero/<int:item_id>', methods=['DELETE'])
@require_auth
def delete_hero(item_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        # Fetch the slide to extract and delete all associated images
        res = supabase.table('hero_backgrounds').select('*').eq('id', item_id).execute()
        if res.data and len(res.data) > 0:
            slide = res.data[0]
            files_to_delete = []
            
            for key in ['bucket_image_url', 'house_bg_url', 'house_bg_mobile_url']:
                if slide.get(key) and 'nanco-assets/' in slide[key]:
                    file_name = slide[key].split('nanco-assets/')[-1]
                    if file_name:
                        files_to_delete.append(file_name)
            
            if files_to_delete:
                supabase.storage.from_('nanco-assets').remove(files_to_delete)

        supabase.table('hero_backgrounds').delete().eq('id', item_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hero/<int:item_id>', methods=['PUT'])
@require_auth
def update_hero(item_id):
    """Update settings for a specific hero background slide."""
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        try:
            res = supabase.table('hero_backgrounds').update(data).eq('id', item_id).execute()
            return jsonify(res.data)
        except Exception as update_err:
            safe_data = {k: v for k, v in data.items() if not k.endswith('_color')}
            res = supabase.table('hero_backgrounds').update(safe_data).eq('id', item_id).execute()
            return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- HERO SETTINGS ENDPOINTS ---

@app.route('/api/hero-settings', methods=['GET'])
def get_hero_settings():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        try:
            res = supabase.table('hero_settings').select('*').limit(1).execute()
            if res.data and len(res.data) > 0:
                return jsonify(res.data[0])
        except Exception as e:
            pass # Table might not exist or columns might be missing
            
        # Return defaults if no row exists
        return jsonify({
            "bg_color": "#c8d90f",
            "overlay_color": "#c8d90f",
            "tag_text": "ISO 9001-2015 Certified",
            "headline": "Paint for Better Lives.",
            "sub_text": "Nanco Paints brings premium-quality, certified paints to homes, offices, and factories across Kerala. Bold colours. Lasting finish.",
            "bucket_image_url": "assets/HERO-PAINT.png",
            "house_bg_url": "assets/house-bg.png",
            "hide_default_hero": False
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hero-settings', methods=['POST'])
@require_auth
def save_hero_settings():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        try:
            res = supabase.table('hero_settings').select('id').limit(1).execute()
            if res.data and len(res.data) > 0:
                row_id = res.data[0]['id']
                supabase.table('hero_settings').update(data).eq('id', row_id).execute()
            else:
                supabase.table('hero_settings').insert(data).execute()
        except Exception as db_err:
            # Fallback if color columns don't exist
            safe_data = {k: v for k, v in data.items() if not k.endswith('_color')}
            res = supabase.table('hero_settings').select('id').limit(1).execute()
            if res.data and len(res.data) > 0:
                row_id = res.data[0]['id']
                supabase.table('hero_settings').update(safe_data).eq('id', row_id).execute()
            else:
                supabase.table('hero_settings').insert(safe_data).execute()
                
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# PRODUCT BANNERS
# ==========================================
import json
import time

@app.route('/api/product-banners', methods=['GET'])
def get_product_banners():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('product_banners').select('*').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/product-banners', methods=['POST'])
@require_auth
def add_product_banner():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        if 'image_url' not in data:
            return jsonify({"error": "image_url is required"}), 400
        
        # NOTE: Ensure RLS policies on product_banners allow inserts, or use the Service Role Key in .env
        res = supabase.table('product_banners').insert({"image_url": data['image_url']}).execute()
        return jsonify(res.data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/product-banners/<int:banner_id>', methods=['DELETE'])
@require_auth
def delete_product_banner(banner_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        # Get banner to retrieve image_url
        res = supabase.table('product_banners').select('image_url').eq('id', banner_id).execute()
        if res.data and len(res.data) > 0:
            image_url = res.data[0].get('image_url')
            if image_url:
                file_name = image_url.split('/')[-1]
                try:
                    supabase.storage.from_('nanco-assets').remove([file_name])
                except Exception as e:
                    print(f"Failed to delete {file_name} from storage: {e}")
        
        # Delete from table
        supabase.table('product_banners').delete().eq('id', banner_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# PRODUCT VIDEOS (Shorts)
# ==========================================

@app.route('/api/videos', methods=['GET'])
def get_videos():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        res = supabase.table('product_videos').select('*').order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/videos', methods=['POST'])
@require_auth
def add_video():
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        if 'video_url' not in data:
            return jsonify({"error": "video_url is required"}), 400
        
        # NOTE: Ensure RLS policies on product_videos allow inserts, or use the Service Role Key in .env
        insert_data = {
            "video_url": data['video_url'],
            "link_url": data.get('link_url') or '../nanco/colors.html'
        }
        res = supabase.table('product_videos').insert(insert_data).execute()
        return jsonify(res.data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/videos/<int:video_id>', methods=['DELETE'])
@require_auth
def delete_video(video_id):
    if not supabase: return jsonify({"error": "Supabase not configured"}), 500
    try:
        # Get video to retrieve video_url
        res = supabase.table('product_videos').select('video_url').eq('id', video_id).execute()
        if res.data and len(res.data) > 0:
            video_url = res.data[0].get('video_url')
            if video_url:
                file_name = video_url.split('/')[-1]
                try:
                    supabase.storage.from_('nanco-assets').remove([file_name])
                except Exception as e:
                    print(f"Failed to delete {file_name} from storage: {e}")
        
        # Delete from table
        supabase.table('product_videos').delete().eq('id', video_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- AUTH ENDPOINTS ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username_or_email = data.get('username', '')
    password = data.get('password', '')

    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'nanco-admin-pass')

    # 1. Check admin credentials first
    if username_or_email == admin_username and password == admin_password:
        return jsonify({
            'token': ADMIN_TOKEN,
            'role': 'admin',
            'name': 'Admin'
        })

    # 2. Check regular users in Supabase
    if supabase:
        try:
            result = supabase.table('users').select('*').eq('email', username_or_email).execute()
            if result.data and len(result.data) > 0:
                user = result.data[0]
                stored_hash = user.get('password_hash', '').encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return jsonify({
                        'token': f"user-{user['id']}-{ADMIN_TOKEN[:8]}",
                        'role': user.get('role', 'user'),
                        'name': user.get('name', 'User'),
                        'email': user.get('email', '')
                    })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/product-media/upload', methods=['POST'])
def upload_product_media():
    if not supabase:
        return jsonify({'error': 'Database not configured'}), 500
        
    product_id = request.form.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    # Create a local uploads directory in the frontend's product_imgs folder
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'product_imgs', 'custom_uploads', str(product_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    uploaded_urls = []

    def save_and_record(file_obj, media_type):
        filename = f"{uuid.uuid4().hex}_{file_obj.filename}"
        
        # Read the file content
        file_content = file_obj.read()
        file_obj.seek(0)
        
        storage_path = f"{product_id}/{filename}"
        
        # Upload to Supabase Storage
        supabase.storage.from_('product-media').upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file_obj.content_type}
        )
        
        # Get public URL
        url = supabase.storage.from_('product-media').get_public_url(storage_path)
        
        # Insert into database (removed 'caption' to fix PGRST204)
        res = supabase.table('product_media').insert({
            'item_id': product_id,
            'url': url,
            'type': media_type
        }).execute()
        
        uploaded_urls.append(url)
        return url

    try:
        # Process banners
        for file in request.files.getlist('banner'):
            if file: save_and_record(file, 'banner')
            
        # Process images
        for file in request.files.getlist('images'):
            if file: save_and_record(file, 'image')
            
        # Process videos
        for file in request.files.getlist('videos'):
            if file: save_and_record(file, 'video')
            
    except Exception as e:
        print("Upload failed:", e)
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': True, 'urls': uploaded_urls})

@app.route('/api/product-media/save-link', methods=['POST'])
def save_media_link():
    if not supabase:
        return jsonify({'error': 'Database not configured'}), 500
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        url = data.get('url')
        media_type = data.get('type', 'image')

        if not product_id or not url:
            return jsonify({'error': 'product_id and url are required'}), 400

        res = supabase.table('product_media').insert({
            'item_id': product_id,
            'url': url,
            'type': media_type
        }).execute()

        return jsonify({'success': True, 'data': res.data})
    except Exception as e:
        print("Save link error:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/product-media/<product_id>', methods=['GET'])
def get_product_media(product_id):
    if not supabase:
        return jsonify({'error': 'Database not configured'}), 500
    try:
        res = supabase.table('product_media').select('*').eq('item_id', product_id).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/product-media/<media_id>', methods=['DELETE'])
def delete_product_media(media_id):
    if not supabase:
        return jsonify({'error': 'Database not configured'}), 500
    try:
        # First get the media to delete the file from storage
        res = supabase.table('product_media').select('url').eq('id', media_id).execute()
        if res.data and len(res.data) > 0:
            url = res.data[0]['url']
            
            # The URL is the full public URL. We need to extract the path inside the bucket.
            # Example: https://sawbglsfqyayuysqcjto.supabase.co/storage/v1/object/public/product-media/product_id/filename.jpg
            # We split by 'public/product-media/' and take the second part
            if '/public/product-media/' in url:
                storage_path = url.split('/public/product-media/')[1]
                # Delete from Supabase Storage
                try:
                    supabase.storage.from_('product-media').remove([storage_path])
                except Exception as e:
                    print("Error deleting from storage:", e)
                
        # Delete from Supabase
        supabase.table('product_media').delete().eq('id', media_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/product-instructions/<product_id>', methods=['GET'])
def get_product_instructions(product_id):
    if not supabase:
        return jsonify({'error': 'Database not configured'}), 500
    try:
        res = supabase.table('product_instructions').select('content').eq('item_id', product_id).execute()
        if res.data and len(res.data) > 0:
            return jsonify({'content': res.data[0]['content']})
        return jsonify({'content': ''})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/product-instructions/save', methods=['POST'])
def save_product_instructions():
    if not supabase:
        return jsonify({'error': 'Database not configured'}), 500
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        content = data.get('content', '')

        if not product_id:
            return jsonify({'error': 'product_id is required'}), 400

        # Upsert: update if exists, insert if not
        existing = supabase.table('product_instructions').select('id').eq('item_id', product_id).execute()
        if existing.data and len(existing.data) > 0:
            supabase.table('product_instructions').update({'content': content}).eq('item_id', product_id).execute()
        else:
            supabase.table('product_instructions').insert({'item_id': product_id, 'content': content}).execute()

        return jsonify({'success': True})
    except Exception as e:
        print("Save instructions error:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    if not supabase:
        return jsonify({'error': 'Database not configured'}), 500

    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    try:
        # Check if email already exists
        existing = supabase.table('users').select('id').eq('email', email).execute()
        if existing.data and len(existing.data) > 0:
            return jsonify({'error': 'An account with this email already exists'}), 409

        # Hash password with bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert new user
        result = supabase.table('users').insert({
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'role': 'user'
        }).execute()

        if result.data:
            user = result.data[0]
            return jsonify({
                'token': f"user-{user['id']}-{ADMIN_TOKEN[:8]}",
                'role': 'user',
                'name': user['name'],
                'email': user['email']
            })
        else:
            return jsonify({'error': 'Failed to create account'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(port=5000, debug=True)
