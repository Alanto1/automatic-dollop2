// Desktop unit tests for HapticMapper - zone boundaries and pulse timing.
// No external test framework: builds with a bare `g++` (see run_tests.sh),
// no Arduino toolchain needed. Re-run after any HapticMapper.h change to
// confirm nothing broke.

#include "../obstacle_haptic/HapticMapper.h"

#include <cstdio>
#include <cstdint>

namespace {

using Zone = HapticMapper::Zone;

}  // namespace

// Each test function owns a local `passed` bool that CHECK() flips to
// false on the first failed assertion (and prints why) - the convention
// this whole file follows.
#define CHECK(cond)                                                     \
    do {                                                                \
        if (!(cond)) {                                                  \
            std::printf("  FAILED (line %d): %s\n", __LINE__, #cond);   \
            passed = false;                                             \
        }                                                                \
    } while (0)

bool test_Classify_FarZone_WellBeyondThreshold() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(3000) == Zone::Far);
    return passed;
}

bool test_Classify_FarZone_AtExactThreshold() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(HapticMapper::kFarThresholdMm) == Zone::Far);
    return passed;
}

bool test_Classify_MediumZone_JustInsideFarBoundary() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(HapticMapper::kFarThresholdMm - 1) == Zone::Medium);
    return passed;
}

bool test_Classify_MediumZone_AtExactLowerBoundary() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(HapticMapper::kMediumThresholdMm) == Zone::Medium);
    return passed;
}

bool test_Classify_NearZone_JustInsideMediumBoundary() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(HapticMapper::kMediumThresholdMm - 1) == Zone::Near);
    return passed;
}

bool test_Classify_NearZone_AtExactLowerBoundary() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(HapticMapper::kNearThresholdMm) == Zone::Near);
    return passed;
}

bool test_Classify_CriticalZone_JustInsideNearBoundary() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(HapticMapper::kNearThresholdMm - 1) == Zone::Critical);
    return passed;
}

bool test_Classify_InvalidReadings_TreatedAsFar() {
    bool passed = true;
    HapticMapper mapper;
    CHECK(mapper.classify(0) == Zone::Far);
    CHECK(mapper.classify(HapticMapper::kMinValidMm - 1) == Zone::Far);
    return passed;
}

bool test_Update_FarZone_MotorAlwaysOff() {
    bool passed = true;
    HapticMapper mapper;
    uint32_t times[] = {0, 100, 100000};
    for (uint32_t t : times) {
        auto cmd = mapper.update(HapticMapper::kFarThresholdMm, t);
        CHECK(cmd.motorOn == false);
    }
    return passed;
}

bool test_Update_MediumZone_PulseTimingFullCycle() {
    bool passed = true;
    HapticMapper mapper;
    uint16_t distance = HapticMapper::kMediumThresholdMm;
    uint32_t start = 1000;

    auto onCmd = mapper.update(distance, start);
    CHECK(onCmd.motorOn == true);
    CHECK(onCmd.pwmDuty == HapticMapper::kMediumDuty);

    auto offCmd = mapper.update(distance, start + HapticMapper::kMediumPulse.onMs);
    CHECK(offCmd.motorOn == false);

    uint32_t cycle = static_cast<uint32_t>(HapticMapper::kMediumPulse.onMs) +
                      HapticMapper::kMediumPulse.offMs;
    auto onAgainCmd = mapper.update(distance, start + cycle);
    CHECK(onAgainCmd.motorOn == true);
    return passed;
}

bool test_Update_NearZone_PulseTimingFullCycle() {
    bool passed = true;
    HapticMapper mapper;
    uint16_t distance = HapticMapper::kNearThresholdMm;
    uint32_t start = 5000;

    auto onCmd = mapper.update(distance, start);
    CHECK(onCmd.motorOn == true);
    CHECK(onCmd.pwmDuty == HapticMapper::kNearDuty);

    auto offCmd = mapper.update(distance, start + HapticMapper::kNearPulse.onMs);
    CHECK(offCmd.motorOn == false);
    return passed;
}

bool test_Update_CriticalZone_ContinuousOn() {
    bool passed = true;
    HapticMapper mapper;
    uint16_t distance = HapticMapper::kMinValidMm;
    uint32_t times[] = {0, 50, 500, 5000};
    for (uint32_t t : times) {
        auto cmd = mapper.update(distance, t);
        CHECK(cmd.motorOn == true);
        CHECK(cmd.pwmDuty == HapticMapper::kCriticalDuty);
    }
    return passed;
}

bool test_Update_NearZone_CycleShorterThanMedium() {
    bool passed = true;
    uint32_t nearCycle = static_cast<uint32_t>(HapticMapper::kNearPulse.onMs) +
                          HapticMapper::kNearPulse.offMs;
    uint32_t mediumCycle = static_cast<uint32_t>(HapticMapper::kMediumPulse.onMs) +
                            HapticMapper::kMediumPulse.offMs;
    CHECK(nearCycle < mediumCycle);
    return passed;
}

bool test_Update_ZoneTransition_RestartsPulsePhase() {
    bool passed = true;
    HapticMapper mapper;
    uint32_t start = 0;

    // Enter Medium zone, advance into its off-phase.
    mapper.update(HapticMapper::kMediumThresholdMm, start);
    uint32_t midOffPhase = start + HapticMapper::kMediumPulse.onMs + 10;
    auto stillOff = mapper.update(HapticMapper::kMediumThresholdMm, midOffPhase);
    CHECK(stillOff.motorOn == false);

    // Obstacle suddenly gets much closer at that same instant - Near
    // zone should start its own pulse fresh (motor on), not inherit
    // Medium's current off-phase.
    auto afterTransition = mapper.update(HapticMapper::kNearThresholdMm, midOffPhase);
    CHECK(afterTransition.motorOn == true);
    return passed;
}

int main() {
    struct TestCase {
        const char* name;
        bool (*fn)();
    };

    TestCase tests[] = {
        {"Classify_FarZone_WellBeyondThreshold", test_Classify_FarZone_WellBeyondThreshold},
        {"Classify_FarZone_AtExactThreshold", test_Classify_FarZone_AtExactThreshold},
        {"Classify_MediumZone_JustInsideFarBoundary", test_Classify_MediumZone_JustInsideFarBoundary},
        {"Classify_MediumZone_AtExactLowerBoundary", test_Classify_MediumZone_AtExactLowerBoundary},
        {"Classify_NearZone_JustInsideMediumBoundary", test_Classify_NearZone_JustInsideMediumBoundary},
        {"Classify_NearZone_AtExactLowerBoundary", test_Classify_NearZone_AtExactLowerBoundary},
        {"Classify_CriticalZone_JustInsideNearBoundary", test_Classify_CriticalZone_JustInsideNearBoundary},
        {"Classify_InvalidReadings_TreatedAsFar", test_Classify_InvalidReadings_TreatedAsFar},
        {"Update_FarZone_MotorAlwaysOff", test_Update_FarZone_MotorAlwaysOff},
        {"Update_MediumZone_PulseTimingFullCycle", test_Update_MediumZone_PulseTimingFullCycle},
        {"Update_NearZone_PulseTimingFullCycle", test_Update_NearZone_PulseTimingFullCycle},
        {"Update_CriticalZone_ContinuousOn", test_Update_CriticalZone_ContinuousOn},
        {"Update_NearZone_CycleShorterThanMedium", test_Update_NearZone_CycleShorterThanMedium},
        {"Update_ZoneTransition_RestartsPulsePhase", test_Update_ZoneTransition_RestartsPulsePhase},
    };

    int total = static_cast<int>(sizeof(tests) / sizeof(tests[0]));
    int passedCount = 0;
    for (const auto& t : tests) {
        bool ok = t.fn();
        std::printf("[%s] %s\n", ok ? "PASS" : "FAIL", t.name);
        if (ok) ++passedCount;
    }

    std::printf("\n%d/%d tests passed\n", passedCount, total);
    return passedCount == total ? 0 : 1;
}
