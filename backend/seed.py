from datetime import datetime

from sqlalchemy import select

from backend.database import Base, SessionLocal, engine
from backend.models import Deployment, Incident, Service


def seed_database():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing_service = db.scalar(select(Service).limit(1))

        if existing_service:
            print("Database already contains seed data. Nothing added.")
            return

        payment = Service(
            name="payment-api",
            environment="production",
            status="healthy",
            cpu=34,
            memory=48,
        )
        checkout = Service(
            name="checkout-api",
            environment="production",
            status="degraded",
            cpu=89,
            memory=71,
        )
        user_service = Service(
            name="user-service",
            environment="production",
            status="healthy",
            cpu=27,
            memory=39,
        )

        db.add_all([payment, checkout, user_service])
        db.flush()

        db.add_all(
            [
                Deployment(
                    service_id=checkout.id,
                    version="v2.3.1",
                    status="successful",
                    deployed_at=datetime(2026, 9, 27, 12, 58),
                ),
                Deployment(
                    service_id=payment.id,
                    version="v1.8.0",
                    status="successful",
                    deployed_at=datetime(2026, 9, 27, 10, 55),
                ),
            ]
        )

        db.add_all(
            [
                Incident(
                    id=1001,
                    service_id=checkout.id,
                    title="Checkout API High Error Rate",
                    severity="high",
                    status="investigating",
                    detected_at=datetime(2026, 9, 27, 13, 8),
                    summary="Checkout requests are returning increased HTTP 500 errors.",
                    evidence=[
                        "HTTP 500 error rate increased",
                        "CPU usage reached 89%",
                        "Database connections reached 93%",
                        "Backend pod restarted 3 times",
                    ],
                    recent_deployment="checkout-api:v2.3.1",
                ),
                Incident(
                    id=1002,
                    service_id=payment.id,
                    title="Payment API Latency Increase",
                    severity="medium",
                    status="monitoring",
                    detected_at=datetime(2026, 9, 27, 11, 15),
                    summary="Payment API response time temporarily exceeded the normal threshold.",
                    evidence=[
                        "Average latency increased to 1.8 seconds",
                        "No major HTTP error increase detected",
                    ],
                    recent_deployment="payment-api:v1.8.0",
                ),
            ]
        )

        db.commit()
        print("Seeded services, deployments, and incidents successfully.")


if __name__ == "__main__":
    seed_database()
