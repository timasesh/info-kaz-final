# Настройка Supabase Storage для проекта

## Проблема
Медиафайлы загружаются в DigitalOcean Spaces вместо Supabase Storage.

## Решение

### 1. Получите Anon Key из Supabase

1. Зайдите в панель управления Supabase: https://supabase.com/dashboard
2. Выберите ваш проект
3. Перейдите в **Settings** → **API**
4. Скопируйте **anon** ключ (public key)

### 2. Установите переменные окружения

#### Для локальной разработки:
Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# База данных
DATABASE_URL=sqlite:///db.sqlite3

# Supabase
SUPABASE_URL=https://khlfpcspkgttuckedlfy.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Другие API ключи
OPENWEATHER_API_KEY=your-openweather-api-key
```

#### Для продакшена (DigitalOcean App Platform):
Установите переменные окружения в панели DigitalOcean:

- `SUPABASE_URL` - URL вашего Supabase проекта
- `SUPABASE_ANON_KEY` - anon ключ из Supabase

### 3. Создайте бакет в Supabase Storage

1. В панели Supabase перейдите в **Storage**
2. Создайте новый бакет с именем `media`
3. Убедитесь, что бакет публичный (Public bucket)

### 4. Установите библиотеку supabase

```bash
pip install supabase==2.3.4
```

### 5. Перезапустите сервер

После установки переменных окружения перезапустите Django сервер.

## Что было исправлено

1. **storage_backends.py**: Полностью переписан для работы с Supabase Storage API напрямую
2. **settings.py**: 
   - Добавлена поддержка `.env` файла
   - Убраны все AWS-связанные настройки
   - Используется только `SUPABASE_URL` и `SUPABASE_ANON_KEY`
3. **requirements.txt**: Добавлена библиотека `supabase==2.3.4`

## Проверка работы

После настройки:
1. Загрузите файл через админку Django
2. Проверьте URL файла - он должен начинаться с `https://khlfpcspkgttuckedlfy.supabase.co/storage/v1/object/public/media/`
3. Проверьте в панели Supabase Storage, что файл появился в бакете `media`

## Возможные проблемы

1. **"SUPABASE_ANON_KEY не установлен"** - установите переменную окружения
2. **"Бакет не найден"** - создайте бакет `media` в Supabase Storage
3. **"Доступ запрещен"** - убедитесь, что бакет публичный и используете правильный anon ключ
4. **"Библиотека supabase не установлена"** - выполните `pip install supabase==2.3.4`
