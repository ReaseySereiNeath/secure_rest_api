# seed_data.py
from database import SessionLocal
from models import User, Item
from auth import hash_password

def seed_admin_user():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists.")
            return

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),  # default password
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created: username=admin, password=admin123")

    except Exception as e:
        print(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

def seed_demo_items():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("Skipping item seeding — admin user not found.")
            return

        existing_item = db.query(Item).first()
        if existing_item:
            print("Demo items already exist.")
            return

        item1 = Item(title="Welcome Item", description="Example item for admin", owner_id=user.id)
        item2 = Item(title="Sample Task", description="This is just a demo item", owner_id=user.id)
        db.add_all([item1, item2])
        db.commit()
        print("Demo items created successfully.")

    except Exception as e:
        print(f"Failed to seed demo items: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Running database seed...")
    seed_admin_user()
    seed_demo_items()
    print("Seeding complete.")
