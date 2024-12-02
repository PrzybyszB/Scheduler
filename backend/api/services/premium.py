def delete_premium(premium):
    """
    Delete object premium and return his data.
    """
    premium_data = {
        "id": premium.id,
        "name": premium.name,
        "price": premium.price,  
        "description": premium.description
    }
    premium.delete()
    return premium_data