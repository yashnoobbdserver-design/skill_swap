from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SkillSwapRequest
from accounts.models import Notification

@receiver(post_save, sender=SkillSwapRequest)
def create_request_notification(sender, instance, created, **kwargs):
    """Create notification when a new skill swap request is created"""
    if created:
        # Create notification for the recipient
        Notification.objects.create(
            recipient=instance.recipient,
            notification_type='skill_request',
            title='New Skill Swap Request',
            message=f'{instance.requester.get_full_name() or instance.requester.username} wants to learn {instance.offered_skill.skill.name} from you.',
            related_user=instance.requester,
            related_object_id=instance.id
        )