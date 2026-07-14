"""
Tests for purchase order API endpoints.
"""
import pytest


class TestPurchaseOrderEndpoints:
    """Test suite for purchase-order-related endpoints."""

    def test_create_purchase_order(self, client):
        """Test creating a purchase order for a valid backlog item."""
        backlog_response = client.get("/api/backlog")
        backlog_item_id = backlog_response.json()[0]["id"]

        response = client.post("/api/purchase-orders", json={
            "backlog_item_id": backlog_item_id,
            "supplier_name": "Acme Supply Co",
            "quantity": 500,
            "unit_cost": 12.5,
            "expected_delivery_date": "2025-12-01",
            "notes": "Rush order"
        })
        assert response.status_code == 201

        data = response.json()
        assert data["backlog_item_id"] == backlog_item_id
        assert data["supplier_name"] == "Acme Supply Co"
        assert data["quantity"] == 500
        assert data["unit_cost"] == 12.5
        assert data["notes"] == "Rush order"
        assert "id" in data
        assert "status" in data
        assert "created_date" in data

    def test_create_purchase_order_for_nonexistent_backlog_item(self, client):
        """Test creating a purchase order for a backlog item that doesn't exist."""
        response = client.post("/api/purchase-orders", json={
            "backlog_item_id": "nonexistent-id-999",
            "supplier_name": "Acme Supply Co",
            "quantity": 500,
            "unit_cost": 12.5,
            "expected_delivery_date": "2025-12-01"
        })
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_purchase_order_by_backlog_item(self, client):
        """Test retrieving a purchase order by backlog item ID after creating it."""
        backlog_response = client.get("/api/backlog")
        backlog_item_id = backlog_response.json()[1]["id"]

        create_response = client.post("/api/purchase-orders", json={
            "backlog_item_id": backlog_item_id,
            "supplier_name": "Global Parts Inc",
            "quantity": 100,
            "unit_cost": 4.75,
            "expected_delivery_date": "2025-11-15"
        })
        assert create_response.status_code == 201

        response = client.get(f"/api/purchase-orders/{backlog_item_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["backlog_item_id"] == backlog_item_id
        assert data["supplier_name"] == "Global Parts Inc"

    def test_get_purchase_order_for_backlog_item_without_po(self, client):
        """Test retrieving a purchase order for a backlog item that has none."""
        response = client.get("/api/purchase-orders/no-po-for-this-item")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "no purchase order" in data["detail"].lower()

    def test_backlog_reflects_purchase_order_status(self, client):
        """Test that creating a PO flips has_purchase_order on the backlog item."""
        backlog_response = client.get("/api/backlog")
        backlog_items = backlog_response.json()
        target_item = next(item for item in backlog_items if not item["has_purchase_order"])

        client.post("/api/purchase-orders", json={
            "backlog_item_id": target_item["id"],
            "supplier_name": "Reliable Vendors LLC",
            "quantity": 250,
            "unit_cost": 8.0,
            "expected_delivery_date": "2025-12-10"
        })

        updated_backlog = client.get("/api/backlog").json()
        updated_item = next(item for item in updated_backlog if item["id"] == target_item["id"])
        assert updated_item["has_purchase_order"] is True
