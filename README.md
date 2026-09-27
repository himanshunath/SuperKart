# SuperKart Sales Forecast: containerized deployment

Two containers on one Docker network:
- **superkart-backend**: Flask + gunicorn API serving the model on port **7860**
- **superkart-frontend**: Streamlit UI on port **8501**, calling the backend at `http://superkart-backend:7860`

## Run in a GitHub Codespace

```bash
# 1. Create a shared network so the containers can reach each other by name
docker network create superkart-net

# 2. Build and run the backend
docker build -t superkart-backend ./backend_files
docker run -d --name superkart-backend --network superkart-net -p 7860:7860 superkart-backend

# 3. Build and run the frontend
docker build -t superkart-frontend ./frontend_files
docker run -d --name superkart-frontend --network superkart-net -p 8501:8501 superkart-frontend

# 4. Check both are up
docker ps
```

In the **Ports** tab, set ports **7860** and **8501** to **Public**, then open the forwarded URLs.
