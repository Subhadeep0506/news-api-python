from .base_config import Config


class FastAPIConfig(Config):
    DATABASE_URL: str = (
        "postgresql://dummy_owner:S2E1sYicoHyp@ep-dry-flower-a1kehj8t.ap-southeast-1.aws.neon.tech/dummy?sslmode=require"
    )
    DATABASE_URL_TEMBO: str = "postgresql://postgres:ZKimP2eBurGglM4q@positively-useful-puffer.data-1.use1.tembo.io:5432/postgres"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    ALGORITHM = "HS256"
    JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"
    JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"
