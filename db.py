from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_KEY or not SUPABASE_URL:
    raise ValueError("Supabase config missing. Check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)