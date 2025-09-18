import 'package:community_marketplace/features/presentation/providers/onboarding_provider.dart';
import 'package:community_marketplace/features/auth/screens/sign_in_screen.dart';
import 'package:community_marketplace/shared/theme/color_schemas.dart';
import 'package:community_marketplace/features/presentation/models/onboarding_model.dart';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => OnboardingProvider(),
      child: const _OnboardingScreenContent(),
    );
  }
}

class _OnboardingScreenContent extends StatelessWidget {
  const _OnboardingScreenContent();

  @override
  Widget build(BuildContext context) {
    return Consumer<OnboardingProvider>(
      builder: (context, provider, child) {
        return Scaffold(
          body: SafeArea(
            minimum: const EdgeInsets.only(
              bottom: 40,
              left: 20,
              right: 20,
              top: 60,
            ),
            child: Stack(
              children: [
                // * Progress Bar
                Positioned(
                  child: Row(
                    children: provider.pages.asMap().entries.map((entry) {
                      int index = entry.key;
                      return Expanded(
                        child: Container(
                          height: 4,
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          decoration: BoxDecoration(
                            color: provider.currentPage >= index
                                ? AppColors.primary
                                : AppColors.mutedIcon,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),

                // * ภาษา (ไทย | EN)
                Positioned(
                  top: 20,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: AppColors.mutedBorder,
                        width: 1,
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      "ไทย | EN",
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                ),

                // * PageView
                PageView.builder(
                  controller: provider.pageController,
                  itemCount: provider.pages.length,
                  onPageChanged: provider.onPageChanged,
                  itemBuilder: (context, index) {
                    final page = provider.pages[index];
                    return OnboardingContent(page: page);
                  },
                ),

                // * Next / Done
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: SizedBox(
                    width: double.infinity,
                    height: 60,
                    child: FilledButton(
                      onPressed: () {
                        if (provider.isLastPage) {
                          Navigator.pushReplacement(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const SignInScreen(),
                            ),
                          );
                        } else {
                          provider.nextPage();
                        }
                      },
                      child: Text(
                        provider.isLastPage ? "เริ่มใช้งาน" : "ถัดไป",
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class OnboardingContent extends StatefulWidget {
  final OnboardingModel page;

  const OnboardingContent({super.key, required this.page});

  @override
  State<OnboardingContent> createState() => _OnboardingContentState();
}

class _OnboardingContentState extends State<OnboardingContent>
    with TickerProviderStateMixin {
  late AnimationController _iconController;
  late Animation<double> _iconAnimation;

  @override
  void initState() {
    super.initState();
    _iconController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    _iconAnimation = Tween<double>(
      begin: -5.0,
      end: 5.0,
    ).animate(_iconController);
  }

  @override
  void dispose() {
    _iconController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 30),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedBuilder(
              animation: _iconController,
              builder: (context, _) => Transform.translate(
                offset: Offset(0, _iconAnimation.value),
                child: Icon(
                  widget.page.icon,
                  size: 100,
                  color: AppColors.primary,
                ),
              ),
            ),
            const SizedBox(height: 30),
            Text(
              widget.page.title,
              textAlign: TextAlign.center,
              style: Theme.of(
                context,
              ).textTheme.displayLarge!.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 15),
            Text(
              widget.page.description,
              textAlign: TextAlign.center,
              style: Theme.of(
                context,
              ).textTheme.bodyMedium!.copyWith(color: AppColors.textMuted),
            ),
          ],
        ),
      ),
    );
  }
}
