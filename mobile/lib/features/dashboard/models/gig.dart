import 'package:freezed_annotation/freezed_annotation.dart';

part 'gig.freezed.dart';
part 'gig.g.dart';

@freezed
class Gig with _$Gig {
  const factory Gig({
    required String id,
    required String title,
    required String description,
    @Default('') String imageUrl,
    required String category,
    required double minPrice,
    required double maxPrice,
    @Default(0.0) double distance,
    required String location,
    required DateTime createdAt,
    @Default(false) bool isFavorite,
  }) = _Gig;

  const Gig._();

  factory Gig.fromJson(Map<String, dynamic> json) => _$GigFromJson(json);

  String get priceRange => '$minPrice - $maxPrice บาท';
  String get distanceText => '${distance.toStringAsFixed(0)} km';
}
