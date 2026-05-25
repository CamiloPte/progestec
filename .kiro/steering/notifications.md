---
inclusion: manual
---

# Notificaciones al Cliente

> Este documento define **cuándo** y **qué** se le comunica al cliente
> durante el ciclo de vida del ticket. La implementación técnica (SMTP,
> plantillas) se aborda en una spec dedicada.

## Principio

El cliente debe enterarse del estado de su equipo **sin tener que entrar
al portal**. La app es un canal pasivo (consulta), el correo es el canal
activo (push).

## Eventos que disparan notificación

Cada transición de estado genera (o puede generar) una notificación
distinta. Esta tabla es la fuente de verdad:

| Origen → Destino                         | Quién mueve  | Notificar al cliente | Asunto sugerido                              |
|------------------------------------------|--------------|----------------------|----------------------------------------------|
| (creación) → RECEIVED                    | ADVISOR      | ✅ siempre           | "Recibimos tu equipo: ticket #N"             |
| RECEIVED → DIAGNOSING                    | TECHNICIAN   | ❌ (interno)         | —                                            |
| DIAGNOSING → WAITING_APPROVAL            | TECHNICIAN   | ✅ **crítico**       | "Tu presupuesto está listo, requiere tu aprobación" |
| WAITING_APPROVAL → REPAIRING             | CLIENT       | ✅ confirmación      | "Aprobaste el presupuesto, comenzamos la reparación" |
| WAITING_APPROVAL → CANCELLED             | CLIENT       | ✅ confirmación      | "Cancelamos la orden según tu decisión"      |
| DIAGNOSING → REPAIRING (sin aprobación)  | TECHNICIAN   | ⚠️ informativo       | "Iniciamos la reparación de tu equipo"       |
| REPAIRING → WAITING_APPROVAL (re-revisar)| TECHNICIAN   | ✅ **crítico**       | "Necesitamos tu aprobación para un cambio"   |
| REPAIRING → READY                        | TECHNICIAN   | ✅ siempre           | "Tu equipo está listo para retirar"          |
| READY → DELIVERED                        | ADVISOR      | ✅ acuse de recibo   | "Confirmamos la entrega de tu equipo"        |
| DELIVERED → CLOSED                       | ADVISOR      | ❌ (interno)         | —                                            |
| cualquier → CANCELLED (no por cliente)   | ADMIN/ADVISOR| ✅ con motivo        | "Tu ticket fue cancelado"                    |
| CLOSED/CANCELLED → RECEIVED (reapertura) | ADMIN        | ✅ con motivo        | "Reabrimos tu ticket"                        |

## Reglas

1. **Idempotencia**: si la transición se reintenta, la notificación se
   envía una sola vez. Asociar la notificación al evento de cambio de
   estado en `ticket_history`, no al estado actual.

2. **Asincronía**: el envío de email **nunca** bloquea la respuesta HTTP
   al cliente que originó la transición. Usar `BackgroundTasks` de FastAPI.

3. **Failure soft**: si el correo falla, el ticket sigue avanzando. Se
   registra el error en logs pero no se aborta la transición.

4. **Plantillas con datos del ticket**: cada email lleva como mínimo
   tracking_code, cliente, dispositivo, fecha del cambio, y un link al
   portal del cliente para ver detalle.

5. **Opt-out futuro**: dejar previsto un campo `email_notifications_enabled`
   en `users` para que el cliente pueda apagarlas si abusa.

## Transiciones críticas que NO pueden quedarse sin email

Si la implementación se hace por etapas, priorizar estas tres por encima
de todo:

1. **DIAGNOSING → WAITING_APPROVAL**: el cliente debe enterarse para poder
   aprobar/rechazar. Sin esto, los tickets se atascan.
2. **REPAIRING → READY**: el cliente debe pasar a recoger.
3. **(creación) → RECEIVED**: cierra el círculo de "mi equipo está en
   buenas manos".

## Lo que NO va en este steering

- Diseño visual de plantillas → spec dedicada.
- Configuración SMTP → ya existe en `app/core/config.py` (`MAIL_*`).
- Webhooks o notificaciones push → fuera de alcance V1.
