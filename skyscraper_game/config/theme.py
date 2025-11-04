class PremiumTheme:
    """Премиум цветовая схема для игры"""
    
    # Основные цвета
    PRIMARY = (70, 130, 180)        # Стальной синий
    SECONDARY = (65, 185, 130)      # Изумрудный
    ACCENT = (255, 185, 70)         # Золотой
    WARNING = (220, 90, 90)         # Коралловый
    
    # Фоновые цвета
    BACKGROUND = (240, 245, 255)    # Нежно-голубой
    SURFACE = (255, 255, 255)       # Белый
    SURFACE_VARIANT = (245, 248, 255)  # Светло-голубой
    
    # Текст
    TEXT_PRIMARY = (50, 50, 80)     # Темно-синий
    TEXT_SECONDARY = (100, 100, 130) # Серо-синий
    TEXT_DISABLED = (180, 180, 200)  # Серый
    
    # Состояния
    SUCCESS = (65, 185, 130)        # Изумрудный
    ERROR = (220, 90, 90)           # Коралловый
    WARNING = (255, 185, 70)        # Золотой
    
    # Градиенты
    GRADIENTS = {
        'primary': [(80, 150, 220), (100, 170, 240)],
        'success': [(65, 185, 130), (85, 205, 150)],
        'accent': [(255, 185, 70), (255, 205, 100)]
    }
    
    @classmethod
    def get_gradient(cls, gradient_name):
        return cls.GRADIENTS.get(gradient_name, cls.GRADIENTS['primary'])