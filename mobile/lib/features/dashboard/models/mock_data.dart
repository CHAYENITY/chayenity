import '../models/index.dart';

/// Mock data สำหรับทดสอบ Dashboard
class DashboardMockData {
  /// Mock categories
  static final List<Category> mockCategories = [
    const Category(
      id: '1',
      name: 'กำลังมาว่าง',
      nameEn: 'Available Now',
      icon: '⏰',
      gigCount: 12,
    ),
    const Category(
      id: '2',
      name: 'สัตว์เลี้ยง',
      nameEn: 'Pet Care',
      icon: '🐕',
      gigCount: 8,
    ),
    const Category(
      id: '3',
      name: 'จัดปาร์ตี้',
      nameEn: 'Party Planning',
      icon: '🎉',
      gigCount: 15,
    ),
    const Category(
      id: '4',
      name: 'ดูแลเด็ก',
      nameEn: 'Childcare',
      icon: '👶',
      gigCount: 10,
    ),
  ];

  /// Mock gigs
  static final List<Gig> mockGigs = [
    Gig(
      id: '1',
      title: 'เพื่อนกินหมูกระทะ คุยง่าย อีจายจัด',
      description: 'หาเพื่อนไปกินหมูกระทะด้วยกัน บรรยากาศดี คุยสนุก',
      imageUrl: '',
      category: 'กำลังมาว่าง',
      minPrice: 999,
      maxPrice: 2999,
      distance: 7.0,
      location: 'หาดใหญ่',
      createdAt: DateTime.now(),
    ),
    Gig(
      id: '2',
      title: 'รับจัดปาร์ตี้วันเกิด ไม่ธีมแฟนซี มีอาหารทะเล',
      description: 'รับจัดปาร์ตี้วันเกิด บรรยากาศอบอุ่น มีอาหารทะเล',
      imageUrl: '',
      category: 'จัดปาร์ตี้',
      minPrice: 999,
      maxPrice: 2999,
      distance: 10.0,
      location: 'หาดใหญ่',
      createdAt: DateTime.now(),
    ),
    Gig(
      id: '3',
      title: 'พาน้องหมาไปเดิน ดูแลน้องหมา',
      description: 'บริการพาน้องหมาไปเดินเล่น ดูแลด้วยความใส่ใจ',
      imageUrl: '',
      category: 'สัตว์เลี้ยง',
      minPrice: 500,
      maxPrice: 1500,
      distance: 5.0,
      location: 'หาดใหญ่',
      createdAt: DateTime.now(),
    ),
    Gig(
      id: '4',
      title: 'ดูแลเด็กที่บ้าน มีประสบการณ์',
      description: 'มีประสบการณ์ดูแลเด็ก รับผิดชอบ น่าเชื่อถือ',
      imageUrl: '',
      category: 'ดูแลเด็ก',
      minPrice: 800,
      maxPrice: 2000,
      distance: 3.0,
      location: 'หาดใหญ่',
      createdAt: DateTime.now(),
    ),
  ];
}
