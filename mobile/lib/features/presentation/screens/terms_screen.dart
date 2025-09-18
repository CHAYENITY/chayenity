import 'package:community_marketplace/features/presentation/data/terms_data.dart';
import 'package:community_marketplace/features/presentation/services/terms_service.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:community_marketplace/shared/constants/app_constants.dart';
import 'package:community_marketplace/shared/theme/color_schemas.dart';
import 'package:community_marketplace/features/presentation/screens/onboarding_screen.dart';
import 'package:community_marketplace/features/presentation/providers/terms_provider.dart';

class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => TermsProvider(),
      child: _TermsScreenContent(),
    );
  }
}

class _TermsScreenContent extends StatelessWidget {
  final ScrollController _scrollController = ScrollController();

  @override
  Widget build(BuildContext context) {
    return Consumer<TermsProvider>(
      builder: (context, provider, child) {
        return Scaffold(
          appBar: AppBar(
            leading: IconButton(
              icon: const Icon(Icons.arrow_back_ios_new),
              onPressed: () => provider.showExitDialog(context),
            ),
            title: Text(
              'ข้อตกลงและเงื่อนไข',
              style: Theme.of(
                context,
              ).textTheme.displayLarge!.copyWith(color: AppColors.textWhite),
            ),
          ),
          body: Stack(
            children: [
              NotificationListener<ScrollNotification>(
                onNotification: provider.handleScrollNotification,
                child: CustomScrollView(
                  controller: _scrollController,
                  slivers: [
                    SliverPadding(
                      padding: EdgeInsets.all(20),
                      sliver: SliverList(
                        delegate: SliverChildListDelegate([
                          ...termData.map(
                            (section) => _buildTermSection(
                              context,
                              section.title,
                              section.content,
                            ),
                          ),
                          const SizedBox(height: 140),
                        ]),
                      ),
                    ),
                  ],
                ),
              ),
              _buildNavbarSection(context),
            ],
          ),
        );
      },
    );
  }

  Widget _buildTermSection(BuildContext context, title, String content) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(15),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 5),
            Text(
              content,
              style: Theme.of(
                context,
              ).textTheme.bodySmall!.copyWith(color: AppColors.textMuted),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavbarSection(BuildContext context) {
    final provider = Provider.of<TermsProvider>(context);
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Spacer(),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.only(top: 30),
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color.fromARGB(0, 255, 255, 255), Colors.white],
              stops: [0.0, 0.1],
            ),
          ),
          child: SafeArea(
            minimum: const EdgeInsets.only(bottom: 40, left: 20, right: 20),
            child: !provider.showAcceptButtons
                ? SizedBox(
                    width: double.infinity,
                    height: 60,
                    child: OutlinedButton(
                      onPressed: () {
                        _scrollController.animateTo(
                          _scrollController.position.maxScrollExtent,
                          duration: AppConstants.defaultAnimationDuration,
                          curve: Curves.easeOut,
                        );
                      },
                      child: const Text('เลื่อนไปด้านล่าง'),
                    ),
                  )
                : Column(
                    children: [
                      SizedBox(
                        width: double.infinity,
                        height: 60,
                        child: FilledButton(
                          onPressed: () async {
                            await TermsService.acceptTerms(context);
                            if (!context.mounted) return;
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const OnboardingScreen(),
                              ),
                            );
                          },
                          child: Text('ยอมรับ'),
                        ),
                      ),
                      const SizedBox(height: 15),
                      GestureDetector(
                        onTap: () => provider.showExitDialog(context),
                        child: Stack(
                          clipBehavior: Clip.none,
                          alignment: Alignment.center,
                          children: [
                            Text(
                              'ไม่ยอมรับ',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            Positioned(
                              bottom: -2, // ขยับเส้นลงให้มีช่องว่าง
                              left: 0,
                              right: 0,
                              child: Container(
                                height: 1.5,
                                color: Colors.black,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ],
    );
  }
}
