#pragma once

namespace chroma_rviz_plugins::theme
{
    struct Color
    {
        float r;
        float g;
        float b;
        float a;
    };

    // Brand & Status UI Colors
    constexpr auto kEmerald = "#10B981";
    constexpr auto kRed = "#EF4444";
    constexpr auto kAmber = "#F59E0B";
    constexpr auto kBlue = "#3B82F6";
    constexpr auto kSkyBlue = "#38BDF8";

    // UI Backgrounds & Borders
    constexpr auto kSlateBg = "#0F172A";
    constexpr auto kSlatePanel = "#1E293B";
    constexpr auto kSlateCard = "#F1F5F9";
    constexpr auto kSlateBorder = "#334155";
    constexpr auto kSlateBorderL = "#CBD5E1";

    // Text Colors
    constexpr auto kTextLight = "#E2E8F0";
    constexpr auto kTextDark = "#334155";
    constexpr auto kTextMuted = "#64748B";
    constexpr auto kTextMutedL = "#94A3B8";
    constexpr auto kTextMutedD = "#475569";

    // 3D Marker Colors
    constexpr Color kMarkerPending = {0.9f, 0.1f, 0.1f, 0.8f};
    constexpr Color kMarkerConfirmed = {0.1f, 0.9f, 0.1f, 0.8f};
    constexpr Color kMarkerText = {0.2f, 0.2f, 0.2f, 0.8f};
    constexpr Color kMarkerTextDark = {0.3f, 0.3f, 0.3f, 1.0f};

}  // namespace chroma_rviz_plugins::theme