.PHONY: up down test logs status clean

# Start the full stack
up:
	docker compose up --build -d

# Stop everything
down:
	docker compose down

# Stop and remove all data
clean:
	docker compose down -v

# Run integration tests
test:
	docker compose exec eval-harness python3 -m pytest /app/tests/ -v
	python3 -m pytest tests/ -v

# View logs for all services
logs:
	docker compose logs -f

# Check service health
status:
	@echo "=== Gateway ===" && curl -sf http://localhost:8080/health || echo "DOWN"
	@echo "\n=== Episode Store ===" && curl -sf http://localhost:8100/v1/health || echo "DOWN"
	@echo "\n=== Policy Engine ===" && curl -sf http://localhost:8200/v1/health || echo "DOWN"
	@echo "\n=== MinIO ===" && curl -sf http://localhost:9000/minio/health/live || echo "DOWN"
	@echo "\n=== Jaeger ===" && curl -sf http://localhost:16686/ > /dev/null && echo "UP" || echo "DOWN"
