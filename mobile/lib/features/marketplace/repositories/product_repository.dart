import '../../../shared/services/index.dart';

/// 🏪 Product Repository - ตัวอย่างการใช้ global HttpService
class ProductRepository {
  final HttpService _http = HttpService.instance;

  // 🔥 CRUD operations แบบ super simple

  Future<List<Product>> getProducts({
    int page = 1,
    int limit = 20,
    String? category,
    String? search,
  }) async {
    try {
      final params = <String, dynamic>{
        'page': page,
        'limit': limit,
        if (category != null) 'category': category,
        if (search != null) 'search': search,
      };

      final data = await _http.get<Map<String, dynamic>>(
        ApiEndpoints.products,
        params: params,
      );

      return (data['products'] as List)
          .map((json) => Product.fromJson(json))
          .toList();
    } on HttpException catch (e) {
      throw ProductException(e.message);
    }
  }

  Future<Product> getProduct(String productId) async {
    try {
      final data = await _http.get<Map<String, dynamic>>(
        '${ApiEndpoints.products}/$productId',
      );
      return Product.fromJson(data);
    } on HttpException catch (e) {
      throw ProductException(e.message);
    }
  }

  Future<Product> createProduct(Product product) async {
    try {
      final data = await _http.post<Map<String, dynamic>>(
        ApiEndpoints.products,
        data: product.toJson(),
      );
      return Product.fromJson(data);
    } on HttpException catch (e) {
      throw ProductException(e.message);
    }
  }

  Future<Product> updateProduct(String productId, Product product) async {
    try {
      final data = await _http.put<Map<String, dynamic>>(
        '${ApiEndpoints.products}/$productId',
        data: product.toJson(),
      );
      return Product.fromJson(data);
    } on HttpException catch (e) {
      throw ProductException(e.message);
    }
  }

  Future<void> deleteProduct(String productId) async {
    try {
      await _http.delete('${ApiEndpoints.products}/$productId');
    } on HttpException catch (e) {
      throw ProductException(e.message);
    }
  }
}

// 📦 Simple Product Model (ตัวอย่าง)
class Product {
  final String id;
  final String name;
  final String description;
  final double price;
  final String? imageUrl;

  Product({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    this.imageUrl,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      price: (json['price'] as num).toDouble(),
      imageUrl: json['image_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'image_url': imageUrl,
    };
  }
}

class ProductException implements Exception {
  final String message;
  const ProductException(this.message);

  @override
  String toString() => 'ProductException: $message';
}
