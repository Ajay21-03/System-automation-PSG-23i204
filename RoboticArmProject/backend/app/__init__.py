"""
Industrial Intelligence Command Center — Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
import logging
import os

def create_app(config=None):
    app = Flask(__name__)

    # CORS: allow local frontend origins only
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]}})

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    # Apply any passed config overrides
    if config:
        app.config.update(config)

    # Register blueprints
    from app.routes.health      import bp as health_bp
    from app.routes.dashboard   import bp as dashboard_bp
    from app.routes.fleet       import bp as fleet_bp
    from app.routes.monitoring  import bp as monitoring_bp
    from app.routes.analytics   import bp as analytics_bp
    from app.routes.predict     import bp as predict_bp
    from app.routes.maintenance import bp as maintenance_bp
    from app.routes.maint_logs  import bp as maint_logs_bp
    from app.routes.security    import bp as security_bp
    from app.routes.automation  import bp as automation_bp
    from app.routes.logs        import bp as logs_bp
    from app.routes.dataset     import bp as dataset_bp
    from app.routes.model       import bp as model_bp
    from app.routes.system      import bp as system_bp

    for bp in [
        health_bp, dashboard_bp, fleet_bp, monitoring_bp,
        analytics_bp, predict_bp, maintenance_bp, maint_logs_bp,
        security_bp, automation_bp, logs_bp, dataset_bp,
        model_bp, system_bp,
    ]:
        app.register_blueprint(bp)

    return app
