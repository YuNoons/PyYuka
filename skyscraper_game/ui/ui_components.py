# ui_components.py
import pygame

class UIComponent:
    """Базовый класс для всех UI компонентов"""
    def __init__(self, rect):
        self.rect = rect
        self.visible = True
        self.enabled = True
        
    def handle_event(self, event):
        return False
        
    def draw(self, surface):
        pass
        
    def update(self):
        pass

class Button(UIComponent):
    """Кнопка с состоянием наведения и клика"""
    def __init__(self, rect, text, action=None, font=None, colors=None):
        super().__init__(rect)
        self.text = text
        self.action = action
        self.hovered = False
        self.pressed = False
        self.font = font or pygame.font.Font(None, 24)
        self.colors = colors or {
            'normal': (100, 100, 100),
            'hover': (150, 150, 150),
            'pressed': (200, 200, 200),
            'text': (255, 255, 255)
        }
        
    def handle_event(self, event):
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.pressed = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.hovered and event.button == 1:
                if self.action:
                    self.action()
                self.pressed = False
                return True
            self.pressed = False
            
        return False
        
    def draw(self, surface):
        if not self.visible:
            return
            
        # Определяем цвет кнопки
        if not self.enabled:
            color = (200, 200, 200)
        elif self.pressed:
            color = self.colors['pressed']
        elif self.hovered:
            color = self.colors['hover']
        else:
            color = self.colors['normal']
            
        # Рисуем кнопку
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=8)
        
        # Рисуем текст
        text_surface = self.font.render(self.text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class UIManager:
    """Централизованный менеджер UI компонентов"""
    def __init__(self):
        self.components = []
        
    def add_component(self, component):
        """Добавляет компонент в менеджер"""
        self.components.append(component)
        
    def handle_event(self, event):
        """Обрабатывает события для всех компонентов"""
        handled = False
        
        if event.type == pygame.MOUSEMOTION:
            # Сбрасываем hover для всех компонентов
            for component in self.components:
                if hasattr(component, 'hovered'):
                    component.hovered = False
            
            # Устанавливаем hover для компонента под курсором
            for component in reversed(self.components):
                if component.visible and component.enabled and component.rect.collidepoint(event.pos):
                    if hasattr(component, 'hovered'):
                        component.hovered = True
                    break
                    
        # Передаем событие всем компонентам
        for component in reversed(self.components):
            if component.visible and component.enabled:
                if component.handle_event(event):
                    handled = True
                    break
                    
        return handled
    
    def update(self):
        """Обновляет все компоненты"""
        for component in self.components:
            if component.visible:
                component.update()
    
    def draw(self, surface):
        """Отрисовывает все компоненты"""
        for component in self.components:
            if component.visible:
                component.draw(surface)