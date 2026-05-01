import os

import mercadopago

_sdk: mercadopago.SDK | None = None


def _get_sdk() -> mercadopago.SDK:
    global _sdk
    if _sdk is None:
        token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
        if not token:
            raise RuntimeError(
                "MERCADOPAGO_ACCESS_TOKEN nao configurado. "
                "Obtenha em mercadopago.com/developers e adicione ao .env"
            )
        _sdk = mercadopago.SDK(token)
    return _sdk


def create_payment_preference(order_id: str, items: list, customer_email: str) -> dict:
    """Cria preferência de pagamento no Mercado Pago."""
    webhook_url = os.getenv("MP_WEBHOOK_URL", "")
    success_url = os.getenv("MP_SUCCESS_URL", "")
    pending_url = os.getenv("MP_PENDING_URL", "")
    failure_url = os.getenv("MP_FAILURE_URL", "")

    preference_data: dict = {
        "items": items,
        "external_reference": order_id,
        "payer": {"email": customer_email},
    }

    if success_url and pending_url and failure_url:
        preference_data["back_urls"] = {
            "success": success_url,
            "pending": pending_url,
            "failure": failure_url,
        }
        if not success_url.startswith("http://localhost"):
            preference_data["auto_return"] = "approved"

    if webhook_url:
        preference_data["notification_url"] = webhook_url

    result = _get_sdk().preference().create(preference_data)
    response = result["response"]
    if result.get("status") not in (200, 201):
        msg = response.get("message") or response.get("error") or "erro desconhecido"
        raise RuntimeError(f"Mercado Pago {result.get('status')}: {msg}")
    return response


def get_payment_info(payment_id: str) -> dict:
    """Busca detalhes de um pagamento pelo ID."""
    result = _get_sdk().payment().get(payment_id)
    return result["response"]
