"""
MongoDB-based User Services
Example of how to use the new database layer in Django services
"""
from typing import Dict, Any, Optional
from apps.db.mongo import (
    users_collection, 
    validate_object_id,
    DatabaseError,
    ValidationError,
    UserModel
)
from apps.db.mongo.utils import log_database_operation


class UserService:
    """User service using MongoDB collections"""
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user in MongoDB
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Created user document
        """
        try:
            # Validate and create user model
            user_model = UserModel.from_dict(user_data)
            user_model.validate()
            
            # Insert into database
            user_id = users_collection.create_user(user_model.to_dict())
            
            # Log operation
            log_database_operation(
                operation="insert",
                collection="users",
                details={"user_id": user_id, "email": user_data.get("email")}
            )
            
            # Return created user
            created_user = users_collection.find_by_id(user_id)
            return {
                "success": True,
                "user": created_user,
                "message": "User created successfully"
            }
            
        except ValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Validation failed"
            }
        except Exception as e:
            log_database_operation(
                operation="insert_error",
                collection="users",
                details={"error": str(e), "email": user_data.get("email")}
            )
            raise DatabaseError(f"Failed to create user: {e}")
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email
        
        Args:
            email: User email address
            
        Returns:
            User document or None if not found
        """
        try:
            user = users_collection.find_by_email(email.lower().strip())
            
            if user:
                log_database_operation(
                    operation="find",
                    collection="users",
                    details={"email": email, "found": True}
                )
            else:
                log_database_operation(
                    operation="find",
                    collection="users",
                    details={"email": email, "found": False}
                )
            
            return user
            
        except Exception as e:
            log_database_operation(
                operation="find_error",
                collection="users",
                details={"email": email, "error": str(e)}
            )
            raise DatabaseError(f"Failed to get user: {e}")
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User ID (string representation of ObjectId)
            
        Returns:
            User document or None if not found
        """
        try:
            if not validate_object_id(user_id):
                raise ValidationError("Invalid user ID format")
            
            user = users_collection.find_by_id(user_id)
            
            log_database_operation(
                operation="find",
                collection="users",
                details={"user_id": user_id, "found": user is not None}
            )
            
            return user
            
        except ValidationError:
            return None
        except Exception as e:
            log_database_operation(
                operation="find_error",
                collection="users",
                details={"user_id": user_id, "error": str(e)}
            )
            raise DatabaseError(f"Failed to get user: {e}")
    
    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            user_id: User ID
            update_data: Dictionary of fields to update
            
        Returns:
            Update result
        """
        try:
            if not validate_object_id(user_id):
                raise ValidationError("Invalid user ID format")
            
            # Validate update data
            if 'email' in update_data:
                update_data['email'] = update_data['email'].lower().strip()
            
            success = users_collection.update_user(user_id, update_data)
            
            log_database_operation(
                operation="update",
                collection="users",
                details={"user_id": user_id, "success": success}
            )
            
            if success:
                # Return updated user
                updated_user = users_collection.find_by_id(user_id)
                return {
                    "success": True,
                    "user": updated_user,
                    "message": "User updated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "User not found or no changes made"
                }
                
        except ValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Validation failed"
            }
        except Exception as e:
            log_database_operation(
                operation="update_error",
                collection="users",
                details={"user_id": user_id, "error": str(e)}
            )
            raise DatabaseError(f"Failed to update user: {e}")
    
    @staticmethod
    def delete_user(user_id: str) -> Dict[str, Any]:
        """
        Delete user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            Delete result
        """
        try:
            if not validate_object_id(user_id):
                raise ValidationError("Invalid user ID format")
            
            success = users_collection.delete_one({"_id": user_id})
            
            log_database_operation(
                operation="delete",
                collection="users",
                details={"user_id": user_id, "success": success}
            )
            
            if success:
                return {
                    "success": True,
                    "message": "User deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "User not found"
                }
                
        except ValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Validation failed"
            }
        except Exception as e:
            log_database_operation(
                operation="delete_error",
                collection="users",
                details={"user_id": user_id, "error": str(e)}
            )
            raise DatabaseError(f"Failed to delete user: {e}")
    
    @staticmethod
    def list_users(page: int = 1, per_page: int = 20, 
                   role_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        List users with pagination and filtering
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            role_filter: Filter by role (optional)
            
        Returns:
            Paginated list of users
        """
        try:
            # Build filter
            filter_dict = {}
            if role_filter:
                filter_dict["role"] = role_filter
            
            # Get users with pagination
            users = users_collection.find_many(
                filter_dict=filter_dict,
                skip=(page - 1) * per_page,
                limit=per_page,
                sort=[("created_at", -1)]
            )
            
            # Get total count
            total_count = users_collection.count_documents(filter_dict)
            
            log_database_operation(
                operation="list",
                collection="users",
                details={
                    "page": page,
                    "per_page": per_page,
                    "role_filter": role_filter,
                    "count": len(users)
                }
            )
            
            return {
                "success": True,
                "users": users,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            log_database_operation(
                operation="list_error",
                collection="users",
                details={"error": str(e)}
            )
            raise DatabaseError(f"Failed to list users: {e}")


# Example usage in Django views
def example_django_view_usage():
    """Example of how to use UserService in Django views"""
    
    # Create user
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "role": "buyer"
    }
    
    result = UserService.create_user(user_data)
    if result["success"]:
        print(f"User created: {result['user']['name']}")
    else:
        print(f"Error: {result['error']}")
    
    # Get user by email
    user = UserService.get_user_by_email("test@example.com")
    if user:
        print(f"Found user: {user['name']}")
    
    # Update user
    update_result = UserService.update_user(
        user["_id"] if user else "invalid_id",
        {"name": "Updated Name"}
    )
    
    # List users
    users_result = UserService.list_users(page=1, per_page=10, role_filter="buyer")
    if users_result["success"]:
        print(f"Found {len(users_result['users'])} users")
