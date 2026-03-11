from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def base():
    return {
        'Василевская Алина': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/aline.JPG', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp'},
        'Коновалова Настя': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/nasya.png', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp=nastya'},
        'Антонова Ксюша': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/ksusha.jpg', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp=nastya'},
        'Сидоренко Эмилия': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/emily.png', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp=nastya'},
        'Самокиш Ангелина': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/angie.png', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp=nastya'},
        'Шаповалова Адель': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/adely.png', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp=nastya'},
        'Искорцева Полина': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/poline.jpg', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp=nastya'},
        'Ляшевич Соня': {'src': 'https://jhtcwaillrfwthaxukyy.supabase.co/storage/v1/object/public/miss_photos/sonya.jpg', 'link': 'https://t.me/miss_lyceum_lbsu_bot?startapp=nastya'},
    }