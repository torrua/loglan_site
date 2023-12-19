# -*- coding: utf-8 -*-
"""The main module for launching app"""

from app.routes import app

if __name__ == "__main__":
    app.run(debug=True)
