from django.apps import AppConfig


class SkillSessionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "skill_sessions"
    
    def ready(self):
        import skill_sessions.signals
