def queue_email_message(email_message, fail_silently=False, priority=None):
    from django_yubin import constants, models, settings

    if constants.PRIORITY_HEADER in email_message.extra_headers:
        priority = email_message.extra_headers.pop(constants.PRIORITY_HEADER)
        priority = constants.PRIORITIES.get(priority.lower())

    if priority == constants.PRIORITY_EMAIL_NOW:
        if constants.EMAIL_BACKEND_SUPPORT:
            from django.core.mail import get_connection
            from django_mailer.engine import send_message
            connection = get_connection(backend=settings.USE_BACKEND)
            result = send_message(email_message, smtp_connection=connection)
            return (result == constants.RESULT_SENT)
        else:
            return email_message.send()
    count = 0
    for to_email in email_message.recipients():
        message = models.Message.objects.create(
            to_address=to_email, from_address=email_message.from_email,
            subject=email_message.subject,
            encoded_message=email_message.message().as_string())
        queued_message = models.QueuedMessage(message=message)
        if priority:
            queued_message.priority = priority
        queued_message.save()
        count += 1
    return count
