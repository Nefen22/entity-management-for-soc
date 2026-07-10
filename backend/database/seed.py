from backend.database.mongodb import MongoDB
from backend.auth.password import hash_password

roles = [
    {
        "name": "admin",
        "permissions": [
            "graph:view",
            "graph:ingest",
            "graph:enrichment"
        ]
    },
    {
        "name": "user",
        "permissions": [
            "graph:view",
            "graph:enrichment"
        ]
    }
]

users = [
    {
        "username": "admin",
        "password": hash_password("admin123"),
        "role": "admin",
        "tenants": ["all"]
    },
    {
        "username": "user",
        "password": hash_password("user123"),
        "role": "user",
        "tenants": ["google", "internal"]
    }
]


def create_indexes():
    users = MongoDB.collection("users")
    roles = MongoDB.collection("roles")
    users.create_index("username", unique=True)
    roles.create_index("name", unique=True)


def seed_roles():
    roles_db = MongoDB.collection("roles")
    for role in roles:
        roles_db.update_one(
            {"name": role["name"]},
            {"$setOnInsert": role},
            upsert=True
        )


def seed_users():
    users_db = MongoDB.collection("users")
    for user in users:
        users_db.update_one(
            {"username": user["username"]},
            {"$setOnInsert": user},
            upsert=True
        )


def seed_auth():
    create_indexes()
    seed_roles()
    seed_users()