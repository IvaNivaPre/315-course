import sqlite3
import datetime
from typing import List, Optional, Tuple


class Database:
    SCORE_WATCH_VIDEO = 3.0
    SCORE_SUBSCRIBE = 5.0
    SCORE_LIKE = 5.0
    SCORE_DISLIKE = -7.0
    SCORE_COMMENT = 2.0
    
    def __init__(self, db_path: str = "video_platform.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        return conn

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    subscribers_count INTEGER DEFAULT 0,
                    pfp_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            '''
            )

            # Categories
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS Categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            '''
            )

            # Videos
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS Videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    video_path TEXT NOT NULL,
                    category_id INTEGER,
                    thumbnail TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    likes_count INTEGER DEFAULT 0,
                    dislikes_count INTEGER DEFAULT 0,
                    views_count INTEGER DEFAULT 0,
                    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users (id),
                    FOREIGN KEY (category_id) REFERENCES Categories (id)
                )
            '''
            )

            # Tags
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS Tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            '''
            )

            # VideoTags
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS VideoTags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    FOREIGN KEY (video_id) REFERENCES Videos (id),
                    FOREIGN KEY (tag_id) REFERENCES Tags (id),
                    UNIQUE(video_id, tag_id)
                )
            '''
            )

            # Comments
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS Comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES Videos (id),
                    FOREIGN KEY (user_id) REFERENCES Users (id)
                )
            '''
            )

            # Likes
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS Likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    is_like BOOLEAN NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES Videos (id),
                    FOREIGN KEY (user_id) REFERENCES Users (id),
                    UNIQUE(video_id, user_id)
                )
            '''
            )

            # History
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS History (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    watched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    watch_duration INTEGER,
                    FOREIGN KEY (video_id) REFERENCES Videos (id),
                    FOREIGN KEY (user_id) REFERENCES Users (id)
                )
            '''
            )

            # Subscriptions
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS Subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscriber_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subscriber_id) REFERENCES Users (id),
                    FOREIGN KEY (channel_id) REFERENCES Users (id),
                    UNIQUE(subscriber_id, channel_id)
                )
            '''
            )

            # UserPreferences
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS UserPreferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    score REAL DEFAULT 0.0,
                    FOREIGN KEY (user_id) REFERENCES Users (id),
                    FOREIGN KEY (category_id) REFERENCES Categories (id),
                    UNIQUE(user_id, category_id)
                )
            '''
            )

            conn.commit()

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ===
    def create_user(self, username: str, email: str, password: str, pfp_path: str = None) -> int:
        """Создает нового пользователя и возвращает его ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO Users (username, email, password, pfp_path)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password, pfp_path)
            )
            return cursor.lastrowid

    def get_user_info(self, user_id: int) -> Optional[sqlite3.Row]:
        """Получает пользователя по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, pfp_path, subscribers_count FROM Users WHERE id = ?', (user_id,))
            return cursor.fetchone()
    
    def get_user_nickname(self, user_id: int) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM Users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            if result is None:
                return None
            return result[0]
    
    def get_user_subscribers_count(self, user_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT subscribers_count FROM Users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            if result is None:
                return 0
            return result[0]

    def get_user_by_username(self, username: str) -> Optional[sqlite3.Row]:
        """Получает пользователя по имени пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
            return cursor.fetchone()

    def get_user_by_email(self, email: str) -> Optional[sqlite3.Row]:
        """Получает пользователя по email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
            return cursor.fetchone()

    def update_user_pfp(self, user_id: int, pfp_path: str):
        """Обновляет аватар пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE Users SET pfp_path = ? WHERE id = ?', (pfp_path, user_id))

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ВИДЕО ===
    def create_video(self, user_id: int, title: str, description: str, video_path: str,
            category_id: int = None, thumbnail: str = None, duration: int = 0) -> int:
        """Создает новое видео и возвращает его ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO Videos (user_id, title, description, video_path, category_id, thumbnail, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, description, video_path, category_id, thumbnail, duration)
            )
            return cursor.lastrowid
    
    def delete_video(self, video_id: int):
        """Удаляет видео по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Videos WHERE id = ?', (video_id,))
            conn.commit()
    

    def upload_video(self, user_id: int, file_path: str, thumbnail_path: str, title: str, 
                 description: str, category: str, tags: List[str], duration: int) -> int:
        """Загружает новое видео с указанными параметрами"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем существование категории
            cursor.execute('SELECT id FROM Categories WHERE name = ?', (category,))
            category_result = cursor.fetchone()
            
            if not category_result:
                raise ValueError(f"Категория '{category}' не существует")
            
            category_id = category_result['id']
            
            # Создаем запись видео
            video_id = self.create_video(
                user_id=user_id,
                title=title,
                description=description,
                video_path=file_path,
                category_id=category_id,
                thumbnail=thumbnail_path,
                duration=duration
            )
            
            # Обрабатываем теги
            for tag_name in tags:
                # Приводим к lowercase и заменяем пробелы на underscore
                normalized_tag = tag_name.lower().replace(' ', '_')
                
                # Добавляем тег в базу
                tag_id = self.add_tag(normalized_tag)
                
                # Связываем тег с видео
                self.add_video_tag(video_id, tag_id)
            
            return video_id

    def get_video_info(self, video_id: int) -> Optional[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT u.username, v.title, v.video_path, v.description, v.views_count, v.upload_date, v.thumbnail, v.duration
                FROM Videos v
                JOIN Users u ON v.user_id = u.id
                WHERE v.id = ?
            ''', (video_id,)
            )
            return cursor.fetchone()
    
    def get_video_profile_info(self, video_id: int) -> Optional[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT u.subscribers_count, v.likes_count, v.dislikes_count, u.pfp_path
                FROM Videos v
                JOIN Users u ON v.user_id = u.id
                WHERE v.id = ?
            ''', (video_id,)
            )
            return cursor.fetchone()
    
    def get_video_path(self, video_id: int) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT video_path
                FROM Videos
                WHERE id = ?
            ''', (video_id,)
            )
            result = cursor.fetchone()
            if result:
                return result['video_path']
            return None
    
    def get_video_description(self, video_id: int) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT description
                FROM Videos
                WHERE id = ?
            ''', (video_id,)
            )
            result = cursor.fetchone()
            if result:
                return result['description']
            return None

    def get_20_videos_id(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT v.id
                FROM Videos v
                ORDER BY v.upload_date DESC
                LIMIT 20
            '''
            )
            result = cursor.fetchall()
            if not result:
                return None
            return (i['id'] for i in result)

    def get_videos_by_user(self, user_id: int, limit: int = 50) -> List[sqlite3.Row]:
        """Получает видео пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT v.id
                FROM Videos v
                LEFT JOIN Users u ON v.user_id = u.id
                WHERE v.user_id = ?
                ORDER BY v.upload_date DESC
                LIMIT ?
            ''', (user_id, limit)
            )
            result = cursor.fetchall()
            if not result:
                return None
            return (i['id'] for i in result)

    def get_popular_videos(self, limit: int = 20) -> List[sqlite3.Row]:
        """Получает популярные видео (по просмотрам)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT v.id
                FROM Videos v
                LEFT JOIN Users u ON v.user_id = u.id
                LEFT JOIN Categories c ON v.category_id = c.id
                ORDER BY v.views_count DESC, v.likes_count DESC
                LIMIT ?
            ''', (limit,)
            )
            result = cursor.fetchall()
            if not result:
                return None
            return (i['id'] for i in result)

    def search_videos(self, query: str, limit: int = 20) -> List[int]:
        """
        Ищет видео по названию, автору и тегам с ранжированием результатов.
        Возвращает список ID видео, отсортированных по релевантности.
        """
        if not query or not query.strip():
            return []
            
        query = query.strip().lower()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT DISTINCT
                    v.id,
                    v.title,
                    u.username,
                    v.views_count,
                    -- Релевантность по совпадению
                    (
                        -- Точное совпадение в названии (50 баллов)
                        CASE WHEN LOWER(v.title) = ? THEN 50 ELSE 0 END
                        +
                        -- Название начинается с запроса (30 баллов)
                        CASE WHEN LOWER(v.title) LIKE ? THEN 30 ELSE 0 END
                        +
                        -- Название содержит запрос (15 баллов)
                        CASE WHEN LOWER(v.title) LIKE ? THEN 15 ELSE 0 END
                        +
                        -- Точное совпадение автора (40 баллов)
                        CASE WHEN LOWER(u.username) = ? THEN 40 ELSE 0 END
                        +
                        -- Автор начинается с запроса (25 баллов)
                        CASE WHEN LOWER(u.username) LIKE ? THEN 25 ELSE 0 END
                        +
                        -- Автор содержит запрос (10 баллов)
                        CASE WHEN LOWER(u.username) LIKE ? THEN 10 ELSE 0 END
                        +
                        -- Описание содержит запрос (5 баллов)
                        CASE WHEN LOWER(v.description) LIKE ? THEN 5 ELSE 0 END
                        +
                        -- Популярность (логарифмическая, макс 5 баллов)
                        CASE 
                            WHEN v.views_count > 0 THEN MIN(5.0, LOG10(v.views_count + 1))
                            ELSE 0
                        END
                    ) as relevance_score
                FROM Videos v
                JOIN Users u ON v.user_id = u.id
                LEFT JOIN VideoTags vt ON v.id = vt.video_id
                LEFT JOIN Tags t ON vt.tag_id = t.id
                WHERE 
                    LOWER(v.title) LIKE ?
                    OR LOWER(u.username) LIKE ?
                    OR LOWER(v.description) LIKE ?
                    OR LOWER(t.name) LIKE ?
                GROUP BY v.id
                HAVING relevance_score > 0
                ORDER BY relevance_score DESC, v.views_count DESC
                LIMIT ?
                ''',
                (
                    query,                    # точное совпадение названия
                    f'{query}%',              # название начинается с
                    f'%{query}%',             # название содержит
                    query,                    # точное совпадение автора
                    f'{query}%',              # автор начинается с
                    f'%{query}%',             # автор содержит
                    f'%{query}%',             # описание содержит
                    f'%{query}%',             # WHERE: название
                    f'%{query}%',             # WHERE: автор
                    f'%{query}%',             # WHERE: описание
                    f'%{query}%',             # WHERE: теги
                    limit
                )
            )
            results = cursor.fetchall()
            return [row['id'] for row in results] if results else []

    def increment_views(self, video_id: int):
        """Увеличивает счетчик просмотров видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE Videos SET views_count = views_count + 1 WHERE id = ?', (video_id,))

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ЛАЙКАМИ ===
    def add_like(self, video_id: int, user_id: int, is_like: bool = True):
        """Добавляет лайк или дизлайк видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем, есть ли уже реакция
            cursor.execute(
                'SELECT id, is_like FROM Likes WHERE video_id = ? AND user_id = ?',
                (video_id, user_id)
            )
            existing = cursor.fetchone()

            if existing:
                # Если реакция уже есть, обновляем
                old_like = existing['is_like']
                cursor.execute('UPDATE Likes SET is_like = ? WHERE id = ?', (is_like, existing['id']))

                # Обновляем счетчики
                if old_like and not is_like:  # лайк -> дизлайк
                    cursor.execute(
                        'UPDATE Videos SET likes_count = likes_count - 1, dislikes_count = dislikes_count + 1 WHERE id = ?', (
                            video_id,)
                    )
                elif not old_like and is_like:  # дизлайк -> лайк
                    cursor.execute(
                        'UPDATE Videos SET likes_count = likes_count + 1, dislikes_count = dislikes_count - 1 WHERE id = ?', (
                            video_id,)
                    )
            else:
                # Новая реакция
                cursor.execute(
                    'INSERT INTO Likes (video_id, user_id, is_like) VALUES (?, ?, ?)',
                    (video_id, user_id, is_like)
                )

                # Обновляем счетчик
                if is_like:
                    cursor.execute('UPDATE Videos SET likes_count = likes_count + 1 WHERE id = ?', (video_id,))
                else:
                    cursor.execute('UPDATE Videos SET dislikes_count = dislikes_count + 1 WHERE id = ?', (video_id,))

    def remove_like(self, video_id: int, user_id: int):
        """Удаляет лайк/дизлайк"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT is_like FROM Likes WHERE video_id = ? AND user_id = ?',
                (video_id, user_id)
            )
            like = cursor.fetchone()

            if like:
                cursor.execute(
                    'DELETE FROM Likes WHERE video_id = ? AND user_id = ?',
                    (video_id, user_id)
                )

                # Обновляем счетчик
                if like['is_like']:
                    cursor.execute('UPDATE Videos SET likes_count = likes_count - 1 WHERE id = ?', (video_id,))
                else:
                    cursor.execute('UPDATE Videos SET dislikes_count = dislikes_count - 1 WHERE id = ?', (video_id,))

    def get_user_like(self, video_id: int, user_id: int) -> Optional[bool]:
        """Получает реакцию пользователя на видео (True - лайк, False - дизлайк, None - нет реакции)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT is_like FROM Likes WHERE video_id = ? AND user_id = ?',
                (video_id, user_id)
            )
            result = cursor.fetchone()
            return result['is_like'] if result else None

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ПОДПИСКАМИ ===
    def add_subscription(self, subscriber_id: int, channel_id: int):
        """Добавляет подписку на канал"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO Subscriptions (subscriber_id, channel_id) VALUES (?, ?)',
                    (subscriber_id, channel_id)
                )
                # Увеличиваем счетчик подписчиков
                cursor.execute(
                    'UPDATE Users SET subscribers_count = subscribers_count + 1 WHERE id = ?',
                    (channel_id,)
                )
            except sqlite3.IntegrityError:
                pass  # Уже подписан

    def remove_subscription(self, subscriber_id: int, channel_id: int):
        """Удаляет подписку на канал"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM Subscriptions WHERE subscriber_id = ? AND channel_id = ?',
                (subscriber_id, channel_id)
            )
            # Уменьшаем счетчик подписчиков
            cursor.execute(
                'UPDATE Users SET subscribers_count = subscribers_count - 1 WHERE id = ?',
                (channel_id,)
            )

    def is_subscribed(self, subscriber_id: int, channel_id: int) -> bool:
        """Проверяет, подписан ли пользователь на канал"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM Subscriptions WHERE subscriber_id = ? AND channel_id = ?',
                (subscriber_id, channel_id)
            )
            return cursor.fetchone() is not None

    def get_user_subscriptions(self, user_id: int) -> List[sqlite3.Row]:
        """Получает каналы, на которые подписан пользователь"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT u.* 
                FROM Users u
                JOIN Subscriptions s ON u.id = s.channel_id
                WHERE s.subscriber_id = ?
                ORDER BY s.subscribed_at DESC
            ''', (user_id,)
            )
            return cursor.fetchall()

    def get_channel_subscribers(self, channel_id: int) -> List[sqlite3.Row]:
        """Получает подписчиков канала"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT u.* 
                FROM Users u
                JOIN Subscriptions s ON u.id = s.subscriber_id
                WHERE s.channel_id = ?
                ORDER BY s.subscribed_at DESC
            ''', (channel_id,)
            )
            return cursor.fetchall()

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ИСТОРИЕЙ ===
    def add_to_history(self, video_id: int, user_id: int, watch_duration: int = 0):
        """Добавляет видео в историю просмотров"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO History (video_id, user_id, watch_duration)
                VALUES (?, ?, ?)
            ''', (video_id, user_id, watch_duration)
            )

    def get_user_history(self, user_id: int, limit: int = 50) -> List[sqlite3.Row]:
        """Получает историю просмотров пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT h.*, v.*, u.username, u.pfp_path
                FROM History h
                JOIN Videos v ON h.video_id = v.id
                JOIN Users u ON v.user_id = u.id
                WHERE h.user_id = ?
                ORDER BY h.watched_at DESC
                LIMIT ?
            ''', (user_id, limit)
            )
            return cursor.fetchall()
    
    def search_user_history(self, user_id: int, query: str, limit: int = 50) -> List[sqlite3.Row]:
        """
        Ищет видео в истории просмотров пользователя по названию, автору и тегам.
        Возвращает результаты с сортировкой по релевантности и дате просмотра.
        """
        if not user_id or not query or not query.strip():
            return []
            
        query = query.strip().lower()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT DISTINCT
                    h.*,
                    v.*,
                    u.username,
                    u.pfp_path,
                    (
                        -- Точное совпадение в названии (50 баллов)
                        CASE WHEN LOWER(v.title) = ? THEN 50 ELSE 0 END
                        +
                        -- Название начинается с запроса (30 баллов)
                        CASE WHEN LOWER(v.title) LIKE ? THEN 30 ELSE 0 END
                        +
                        -- Название содержит запрос (15 баллов)
                        CASE WHEN LOWER(v.title) LIKE ? THEN 15 ELSE 0 END
                        +
                        -- Точное совпадение автора (40 баллов)
                        CASE WHEN LOWER(u.username) = ? THEN 40 ELSE 0 END
                        +
                        -- Автор начинается с запроса (25 баллов)
                        CASE WHEN LOWER(u.username) LIKE ? THEN 25 ELSE 0 END
                        +
                        -- Автор содержит запрос (10 баллов)
                        CASE WHEN LOWER(u.username) LIKE ? THEN 10 ELSE 0 END
                    ) as relevance_score
                FROM History h
                JOIN Videos v ON h.video_id = v.id
                JOIN Users u ON v.user_id = u.id
                LEFT JOIN VideoTags vt ON v.id = vt.video_id
                LEFT JOIN Tags t ON vt.tag_id = t.id
                WHERE 
                    h.user_id = ?
                    AND (
                        LOWER(v.title) LIKE ?
                        OR LOWER(u.username) LIKE ?
                        OR LOWER(t.name) LIKE ?
                    )
                GROUP BY h.id
                HAVING relevance_score > 0
                ORDER BY relevance_score DESC, h.watched_at DESC
                LIMIT ?
                ''',
                (
                    query,                    # точное совпадение названия
                    f'{query}%',              # название начинается с
                    f'%{query}%',             # название содержит
                    query,                    # точное совпадение автора
                    f'{query}%',              # автор начинается с
                    f'%{query}%',             # автор содержит
                    user_id,                  # WHERE: user_id
                    f'%{query}%',             # WHERE: название
                    f'%{query}%',             # WHERE: автор
                    f'%{query}%',             # WHERE: теги
                    limit
                )
            )
            return cursor.fetchall()

    # === МЕТОДЫ ДЛЯ РАБОТЫ С КОММЕНТАРИЯМИ ===
    def add_comment(self, video_id: int, user_id: int, text: str) -> int:
        """Добавляет комментарий к видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO Comments (video_id, user_id, text)
                VALUES (?, ?, ?)
            ''', (video_id, user_id, text)
            )
            return cursor.lastrowid

    def get_video_comments(self, video_id: int) -> List[sqlite3.Row]:
        """Получает комментарии к видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT c.*, u.username, u.pfp_path
                FROM Comments c
                JOIN Users u ON c.user_id = u.id
                WHERE c.video_id = ?
                ORDER BY c.created_at DESC
            ''', (video_id,)
            )
            return cursor.fetchall()

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ТЕГАМИ ===
    def add_tag(self, name: str) -> int:
        """Добавляет тег и возвращает его ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO Tags (name) VALUES (?)', (name,))
            except sqlite3.IntegrityError:
                # Тег уже существует
                cursor.execute('SELECT id FROM Tags WHERE name = ?', (name,))
                return cursor.fetchone()['id']
            return cursor.lastrowid

    def add_video_tag(self, video_id: int, tag_id: int):
        """Добавляет тег к видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO VideoTags (video_id, tag_id) VALUES (?, ?)',
                    (video_id, tag_id)
                )
            except sqlite3.IntegrityError:
                pass  # Тег уже добавлен

    def get_video_tags(self, video_id: int) -> List[sqlite3.Row]:
        """Получает теги видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT t.*
                FROM Tags t
                JOIN VideoTags vt ON t.id = vt.tag_id
                WHERE vt.video_id = ?
            ''', (video_id,)
            )
            return cursor.fetchall()

    # === МЕТОДЫ ДЛЯ РАБОТЫ С КАТЕГОРИЯМИ ===
    def add_category(self, name: str) -> int:
        """Добавляет категорию и возвращает ее ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO Categories (name) VALUES (?)', (name,))
            except sqlite3.IntegrityError:
                # Категория уже существует
                cursor.execute('SELECT id FROM Categories WHERE name = ?', (name,))
                return cursor.fetchone()['id']
            return cursor.lastrowid

    def get_all_categories_names(self) -> List[str]:
        """Получает все категории"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM Categories ORDER BY name')
            return [row['name'] for row in cursor.fetchall()]

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    def get_liked_videos(self, user_id: int) -> List[sqlite3.Row]:
        """Получает лайкнутые видео пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT v.*, u.username, u.pfp_path
                FROM Videos v
                JOIN Likes l ON v.id = l.video_id
                JOIN Users u ON v.user_id = u.id
                WHERE l.user_id = ? AND l.is_like = 1
                ORDER BY l.timestamp DESC
            ''', (user_id,)
            )
            return cursor.fetchall()
    
    def delete_all_categories(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Categories')
            conn.commit()
    
    def create_categories(self):
        self.delete_all_categories()
        
        video_categories = {
            "Образование и обучение": [
                "Лекции и уроки",
                "Научпоп",
                "Языки и лингвистика",
                "Онлайн-курсы",
                "История и культура",
                "Карьера и саморазвитие"
            ],
            "Развлечения": [
                "Комедия и юмор",
                "Шоу и челленджи",
                "Интервью и подкасты",
                "Реалити-контент",
                "Мемы и скетчи",
                "Анимация"
            ],
            "Фильмы и сериалы": [
                "Трейлеры",
                "Обзоры и реакции",
                "Полнометражные фильмы",
                "Сериалы",
                "Короткометражки и независимые проекты"
            ],
            "Игры": [
                "Геймплей и стримы",
                "Обзоры игр",
                "Гайды и советы",
                "Киберспорт и турниры",
                "Игровые новости"
            ],
            "Музыка": [
                "Музыкальные клипы",
                "Живые выступления",
                "Каверы и ремиксы",
                "Музыкальные подборки",
                "Саундтреки"
            ],
            "Быт и хобби": [
                "Кулинария",
                "DIY и рукоделие",
                "Дом и сад",
                "Путешествия и влоги",
                "Домашние животные"
            ],
            "Здоровье и спорт": [
                "Тренировки и фитнес",
                "Йога и медитация",
                "Питание и диеты",
                "Спортивные соревнования"
            ],
            "Мотивация и личностный рост": [
                "Психология",
                "Саморазвитие",
                "Истории успеха",
                "Философия и мышление"
            ],
            "Технологии и наука": [
                "Гаджеты и обзоры техники",
                "Программирование и IT",
                "Искусственный интеллект",
                "Научные открытия",
                "Космос и астрономия"
            ],
            "Новости и общество": [
                "Мировые и локальные новости",
                "Аналитика и мнения",
                "Социальные темы",
                "Документальные видео"
            ]
        }


        for _, category in video_categories.items():
            for subcategory in category:
                self.add_category(subcategory)

    def get_video_path(self, video_id):
        """Получает путь к видеофайлу"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT video_path FROM Videos WHERE id=?", (video_id,))
            result = cursor.fetchone()
            return result['video_path'] if result else ""

    def get_video_description(self, video_id):
        """Получает описание видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM Videos WHERE id=?", (video_id,))
            result = cursor.fetchone()
            return result['description'] if result else ""

    def get_author_subscribers(self, username):
        """Получает количество подписчиков автора по username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subscribers_count FROM Users WHERE username=?", (username,))
            result = cursor.fetchone()
            return result['subscribers_count'] if result else 0

    def get_video_likes(self, video_id):
        """Получает количество лайков видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT likes_count FROM Videos WHERE id=?", (video_id,))
            result = cursor.fetchone()
            return result['likes_count'] if result else 0

    def get_video_dislikes(self, video_id):
        """Получает количество дизлайков видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT dislikes_count FROM Videos WHERE id=?", (video_id,))
            result = cursor.fetchone()
            return result['dislikes_count'] if result else 0

    def get_author_avatar_by_username(self, username):
        """Получает путь к аватару автора по username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pfp_path FROM Users WHERE username=?", (username,))
            result = cursor.fetchone()
            return result['pfp_path'] if result else "icons/default_avatar.png"

    def add_to_watch_history(self, user_id, video_id, watch_duration=0):
        """Добавляет или обновляет видео в истории просмотров"""
        if watch_duration is None:
            watch_duration = 0
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Ищем последнюю запись для этого видео (не старше 1 часа)
            cursor.execute(
                """
                SELECT id, watched_at FROM History 
                WHERE user_id=? AND video_id=? 
                AND datetime(watched_at) > datetime('now', '-1 hour')
                ORDER BY watched_at DESC LIMIT 1
                """,
                (user_id, video_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Обновляем существующую запись
                cursor.execute(
                    "UPDATE History SET watch_duration=?, watched_at=datetime('now') WHERE id=?",
                    (watch_duration, existing['id'])
                )
            else:
                # Создаем новую запись
                cursor.execute(
                    "INSERT INTO History (user_id, video_id, watch_duration, watched_at) VALUES (?, ?, ?, datetime('now'))",
                    (user_id, video_id, watch_duration)
                )
            conn.commit()

    def get_user_id_by_username(self, username):
        """Получает ID пользователя по username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Users WHERE username=?", (username,))
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def get_watch_duration(self, user_id: int, video_id: int) -> int:
        """Получает сохраненное время просмотра видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT watch_duration FROM History WHERE user_id=? AND video_id=? ORDER BY watched_at DESC LIMIT 1",
                (user_id, video_id)
            )
            result = cursor.fetchone()
            return result['watch_duration'] if result else 0
    
    def cleanup_history_duplicates(self):
        """Очищает дубликаты в истории, оставляя только последнюю запись для каждого видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM History 
                WHERE id NOT IN (
                    SELECT MAX(id) 
                    FROM History 
                    GROUP BY user_id, video_id
                )
                """
            )
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

    # Методы для работы с подписками
    def is_subscribed(self, subscriber_id: int, channel_id: int) -> bool:
        """Проверяет, подписан ли пользователь на канал"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM Subscriptions WHERE subscriber_id=? AND channel_id=?",
                (subscriber_id, channel_id)
            )
            return cursor.fetchone() is not None

    def subscribe(self, subscriber_id: int, channel_id: int):
        if subscriber_id == channel_id:
            return
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Subscriptions (subscriber_id, channel_id) VALUES (?, ?)",
                    (subscriber_id, channel_id)
                )
                cursor.execute(
                    "UPDATE Users SET subscribers_count = subscribers_count + 1 WHERE id=?",
                    (channel_id,)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                pass

    def unsubscribe(self, subscriber_id: int, channel_id: int):
        """Отписывает пользователя от канала"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Subscriptions WHERE subscriber_id=? AND channel_id=?",
                (subscriber_id, channel_id)
            )
            if cursor.rowcount > 0:
                cursor.execute(
                    "UPDATE Users SET subscribers_count = subscribers_count - 1 WHERE id=? AND subscribers_count > 0",
                    (channel_id,)
                )
                conn.commit()
            else:
                pass

    def get_channel_id_by_video(self, video_id: int) -> Optional[int]:
        """Получает ID канала (автора) по ID видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Videos WHERE id=?", (video_id,))
            result = cursor.fetchone()
            return result['user_id'] if result else None

    # Методы для работы с лайками/дизлайками
    def get_user_like_status(self, user_id: int, video_id: int) -> Optional[bool]:
        """
        Получает статус оценки пользователя для видео
        Возвращает: None (нет оценки), True (лайк), False (дизлайк)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_like FROM Likes WHERE user_id=? AND video_id=?",
                (user_id, video_id)
            )
            result = cursor.fetchone()
            return bool(result['is_like']) if result else None

    def set_like(self, user_id: int, video_id: int, is_like: bool):
        """
        Устанавливает лайк или дизлайк для видео
        is_like: True для лайка, False для дизлайка
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем текущий статус
            current_status = self.get_user_like_status(user_id, video_id)
            
            if current_status is None:
                # Новая оценка
                cursor.execute(
                    "INSERT INTO Likes (user_id, video_id, is_like) VALUES (?, ?, ?)",
                    (user_id, video_id, is_like)
                )
                # Обновляем счетчик
                if is_like:
                    cursor.execute(
                        "UPDATE Videos SET likes_count = likes_count + 1 WHERE id=?",
                        (video_id,)
                    )
                else:
                    cursor.execute(
                        "UPDATE Videos SET dislikes_count = dislikes_count + 1 WHERE id=?",
                        (video_id,)
                    )
            elif current_status != is_like:
                # Изменяем оценку
                cursor.execute(
                    "UPDATE Likes SET is_like=?, timestamp=datetime('now') WHERE user_id=? AND video_id=?",
                    (is_like, user_id, video_id)
                )
                # Обновляем счетчики
                if is_like:
                    # Было дизлайк, стало лайк
                    cursor.execute(
                        "UPDATE Videos SET likes_count = likes_count + 1, dislikes_count = dislikes_count - 1 WHERE id=?",
                        (video_id,)
                    )
                else:
                    # Было лайк, стало дизлайк
                    cursor.execute(
                        "UPDATE Videos SET likes_count = likes_count - 1, dislikes_count = dislikes_count + 1 WHERE id=?",
                        (video_id,)
                    )
            
            conn.commit()

    def remove_like(self, user_id: int, video_id: int):
        """Убирает оценку пользователя с видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем текущий статус
            current_status = self.get_user_like_status(user_id, video_id)
            
            if current_status is not None:
                cursor.execute(
                    "DELETE FROM Likes WHERE user_id=? AND video_id=?",
                    (user_id, video_id)
                )
                # Обновляем счетчик
                if current_status:
                    cursor.execute(
                        "UPDATE Videos SET likes_count = likes_count - 1 WHERE id=? AND likes_count > 0",
                        (video_id,)
                    )
                else:
                    cursor.execute(
                        "UPDATE Videos SET dislikes_count = dislikes_count - 1 WHERE id=? AND dislikes_count > 0",
                        (video_id,)
                    )
                conn.commit()

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ПРЕДПОЧТЕНИЯМИ ПОЛЬЗОВАТЕЛЯ ===
    def update_user_preference(self, user_id: int, category_id: int, score_delta: float):
        """Обновляет предпочтение пользователя для категории"""
        if not user_id or not category_id:
            return
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем существование записи
            cursor.execute(
                "SELECT score FROM UserPreferences WHERE user_id=? AND category_id=?",
                (user_id, category_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Обновляем существующую запись
                new_score = max(0.0, existing['score'] + score_delta)  # Не позволяем score стать отрицательным
                cursor.execute(
                    "UPDATE UserPreferences SET score=? WHERE user_id=? AND category_id=?",
                    (new_score, user_id, category_id)
                )
            else:
                # Создаем новую запись
                new_score = max(0.0, score_delta)
                cursor.execute(
                    "INSERT INTO UserPreferences (user_id, category_id, score) VALUES (?, ?, ?)",
                    (user_id, category_id, new_score)
                )
            
            conn.commit()
    
    def get_category_id_by_video(self, video_id: int) -> Optional[int]:
        """Получает ID категории по ID видео"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category_id FROM Videos WHERE id=?", (video_id,))
            result = cursor.fetchone()
            return result['category_id'] if result else None
    
    def update_preference_on_watch(self, user_id: int, video_id: int):
        """Обновляет предпочтения при просмотре видео (7+ секунд)"""
        category_id = self.get_category_id_by_video(video_id)
        if category_id:
            self.update_user_preference(user_id, category_id, self.SCORE_WATCH_VIDEO)
    
    def update_preference_on_subscribe(self, user_id: int, channel_id: int):
        """Обновляет предпочтения при подписке на канал"""
        # Находим все категории, в которых автор загружал видео
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT category_id 
                FROM Videos 
                WHERE user_id=? AND category_id IS NOT NULL
                """,
                (channel_id,)
            )
            categories = cursor.fetchall()
            
        # Обновляем предпочтения для каждой категории
        for cat in categories:
            self.update_user_preference(user_id, cat['category_id'], self.SCORE_SUBSCRIBE)
    
    def update_preference_on_like(self, user_id: int, video_id: int, is_like: bool):
        """Обновляет предпочтения при лайке/дизлайке видео"""
        category_id = self.get_category_id_by_video(video_id)
        if category_id:
            score_delta = self.SCORE_LIKE if is_like else self.SCORE_DISLIKE
            self.update_user_preference(user_id, category_id, score_delta)
    
    def update_preference_on_comment(self, user_id: int, video_id: int):
        """Обновляет предпочтения при написании комментария"""
        category_id = self.get_category_id_by_video(video_id)
        if category_id:
            self.update_user_preference(user_id, category_id, self.SCORE_COMMENT)
    
    def get_recommended_videos(self, user_id: int = None, limit: int = 20) -> List[int]:
        """
        Возвращает рекомендованные видео на основе:
        - Популярности (просмотры)
        - Актуальности (дата загрузки)
        - Предпочтений пользователя (если user_id указан)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                # С учетом предпочтений пользователя
                cursor.execute(
                    """
                    SELECT 
                        v.id,
                        v.views_count,
                        v.upload_date,
                        v.category_id,
                        COALESCE(up.score, 0) as preference_score,
                        -- Формула рекомендации:
                        -- Популярность (нормализованная) + Актуальность (дней назад) + Предпочтение
                        (
                            -- Популярность: логарифм просмотров (макс 10 баллов)
                            CASE 
                                WHEN v.views_count > 0 THEN MIN(10.0, LOG10(v.views_count + 1) * 2)
                                ELSE 0
                            END
                            +
                            -- Актуальность: чем новее, тем больше баллов (макс 10 баллов)
                            CASE
                                WHEN JULIANDAY('now') - JULIANDAY(v.upload_date) < 1 THEN 10.0
                                WHEN JULIANDAY('now') - JULIANDAY(v.upload_date) < 7 THEN 7.0
                                WHEN JULIANDAY('now') - JULIANDAY(v.upload_date) < 30 THEN 4.0
                                ELSE 1.0
                            END
                            +
                            -- Предпочтения пользователя (нормализованные, макс 10 баллов)
                            MIN(10.0, COALESCE(up.score, 0) / 10.0)
                        ) as recommendation_score
                    FROM Videos v
                    LEFT JOIN UserPreferences up
                        ON v.category_id = up.category_id AND up.user_id = ?
                    ORDER BY recommendation_score DESC, v.upload_date DESC
                    LIMIT ?
                    """,
                    (user_id, limit)
                )
            else:
                # Без учета предпочтений (для неавторизованных пользователей)
                cursor.execute(
                    """
                    SELECT 
                        v.id,
                        (
                            -- Популярность
                            CASE 
                                WHEN v.views_count > 0 THEN MIN(10.0, LOG10(v.views_count + 1) * 2)
                                ELSE 0
                            END
                            +
                            -- Актуальность
                            CASE
                                WHEN JULIANDAY('now') - JULIANDAY(v.upload_date) < 1 THEN 10.0
                                WHEN JULIANDAY('now') - JULIANDAY(v.upload_date) < 7 THEN 7.0
                                WHEN JULIANDAY('now') - JULIANDAY(v.upload_date) < 30 THEN 4.0
                                ELSE 1.0
                            END
                        ) as recommendation_score
                    FROM Videos v
                    ORDER BY recommendation_score DESC, v.upload_date DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
            
            results = cursor.fetchall()
            return [row['id'] for row in results] if results else []
            
    
    def clear_all_data(self):
        """Удаляет все данные из всех таблиц базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Отключаем проверку внешних ключей для удаления в любом порядке
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            # Удаляем данные из всех таблиц
            cursor.execute("DELETE FROM VideoTags")
            cursor.execute("DELETE FROM Comments")
            cursor.execute("DELETE FROM Likes")
            cursor.execute("DELETE FROM History")
            cursor.execute("DELETE FROM Subscriptions")
            cursor.execute("DELETE FROM UserPreferences")
            cursor.execute("DELETE FROM Videos")
            cursor.execute("DELETE FROM Tags")
            cursor.execute("DELETE FROM Categories")
            cursor.execute("DELETE FROM Users")
            
            # Включаем проверку внешних ключей обратно
            cursor.execute("PRAGMA foreign_keys = ON")
            
            conn.commit()

    def close(self):
        if hasattr(self, 'conn'):
            self.conn.close()
