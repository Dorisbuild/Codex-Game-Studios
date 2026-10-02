# Unreal Engine 5.7 — UI Module Reference

**Last verified:** 2026-02-13
**Knowledge Gap:** UE 5.7 UMG and CommonUI improvements

---

## Overview

UE 5.7 UI systems:
- **UMG (Unreal Motion Graphics)**: Visual question-based UI (RECOMMENDED)
- **CommonUI**: Cross-platform input-aware UI framework (console/PC)
- **Slate**: Low-level C++ UI (engine/editor UI)

---

## UMG (Unreal Motion Graphics)

### Create Question Blueprint

1. Content Browser > User Interface > Question Blueprint
2. Open Question Designer
3. Drag questions from Palette: Button, Text, Image, ProgressBar, etc.

---

## Basic UMG Setup in C++

### Create and Display Question

```cpp
#include "Blueprint/UserQuestion.h"

UPROPERTY(EditAnywhere, Category = "UI")
TSubclassOf<UUserQuestion> HealthBarQuestionClass;

void AMyCharacter::BeginPlay() {
    Super::BeginPlay();

    // Create question
    UUserQuestion* HealthBarQuestion = CreateQuestion<UUserQuestion>(GetWorld(), HealthBarQuestionClass);

    // Add to viewport
    HealthBarQuestion->AddToViewport();
}
```

### Remove Question

```cpp
HealthBarQuestion->RemoveFromParent();
```

---

## Access Question Elements from C++

### Bind to Question Elements

```cpp
UCLASS()
class UMyHealthQuestion : public UUserQuestion {
    GENERATED_BODY()

public:
    // ✅ Bind to question elements (must match names in Question Blueprint)
    UPROPERTY(meta = (BindQuestion))
    TObjectPtr<UTextBlock> HealthText;

    UPROPERTY(meta = (BindQuestion))
    TObjectPtr<UProgressBar> HealthBar;

    void UpdateHealth(int32 CurrentHealth, int32 MaxHealth) {
        HealthText->SetText(FText::FromString(FString::Printf(TEXT("%d / %d"), CurrentHealth, MaxHealth)));
        HealthBar->SetPercent((float)CurrentHealth / MaxHealth);
    }
};
```

---

## Common UMG Questions

### Text Block

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UTextBlock> ScoreText;

ScoreText->SetText(FText::FromString(TEXT("Score: 100")));
ScoreText->SetColorAndOpacity(FLinearColor::Green);
```

### Button

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UButton> PlayButton;

void NativeConstruct() override {
    Super::NativeConstruct();

    // Bind button click
    PlayButton->OnClicked.AddDynamic(this, &UMyMenuQuestion::OnPlayClicked);
}

UFUNCTION()
void OnPlayClicked() {
    UE_LOG(LogTemp, Warning, TEXT("Play clicked"));
}
```

### Image

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UImage> PlayerAvatar;

PlayerAvatar->SetBrushFromTexture(AvatarTexture);
PlayerAvatar->SetColorAndOpacity(FLinearColor::White);
```

### Progress Bar

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UProgressBar> HealthBar;

HealthBar->SetPercent(0.75f); // 75%
HealthBar->SetFillColorAndOpacity(FLinearColor::Red);
```

### Slider

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<USlider> VolumeSlider;

void NativeConstruct() override {
    Super::NativeConstruct();
    VolumeSlider->OnValueChanged.AddDynamic(this, &UMyQuestion::OnVolumeChanged);
}

UFUNCTION()
void OnVolumeChanged(float Value) {
    // Value is 0.0 - 1.0
    UE_LOG(LogTemp, Warning, TEXT("Volume: %f"), Value);
}
```

### EditableTextBox (Input Field)

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UEditableTextBox> PlayerNameInput;

void NativeConstruct() override {
    Super::NativeConstruct();
    PlayerNameInput->OnTextChanged.AddDynamic(this, &UMyQuestion::OnNameChanged);
}

UFUNCTION()
void OnNameChanged(const FText& Text) {
    FString PlayerName = Text.ToString();
}
```

---

## UMG Animations

### Play Animation

```cpp
UPROPERTY(Transient, meta = (BindQuestionAnim))
TObjectPtr<UQuestionAnimation> FadeInAnimation;

void ShowUI() {
    PlayAnimation(FadeInAnimation);
}
```

### Stop Animation

```cpp
StopAnimation(FadeInAnimation);
```

---

## Canvas Panel (Layout)

### Canvas Panel (Absolute Positioning)

```cpp
// Use in Question Blueprint for absolute positioning
// Anchor questions to corners/edges for responsive UI
```

### Vertical Box (Stack Vertically)

```cpp
// Auto-stacks children vertically
```

### Horizontal Box (Stack Horizontally)

```cpp
// Auto-stacks children horizontally
```

### Grid Panel (Grid Layout)

```cpp
// Arranges children in a grid
```

---

## World Space UI (3D UI)

### Question Component (3D UI in World)

```cpp
#include "Components/QuestionComponent.h"

UQuestionComponent* HealthBarQuestion = CreateDefaultSubobject<UQuestionComponent>(TEXT("HealthBar"));
HealthBarQuestion->SetupAttachment(RootComponent);
HealthBarQuestion->SetQuestionClass(HealthBarQuestionClass);
HealthBarQuestion->SetQuestionSpace(EQuestionSpace::World); // 3D world space
HealthBarQuestion->SetDrawSize(FVector2D(200, 50));
```

---

## Input Handling in UMG

### Override Keyboard Input

```cpp
UCLASS()
class UMyQuestion : public UUserQuestion {
    GENERATED_BODY()

public:
    virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override {
        if (InKeyEvent.GetKey() == EKeys::Escape) {
            // Handle Escape key
            CloseMenu();
            return FReply::Handled();
        }
        return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
    }
};
```

---

## CommonUI (Cross-Platform Input)

### Enable CommonUI Plugin

```cpp
// Enable: Edit > Plugins > CommonUI
// Restart editor
```

### Use CommonUI Questions

```cpp
// CommonUI questions:
// - CommonActivatableQuestion: Base for screens/menus
// - CommonButtonBase: Input-aware button (gamepad + mouse)
// - CommonTextBlock: Text with styling
```

### CommonActivatableQuestion Example

```cpp
UCLASS()
class UMyMenuQuestion : public UCommonActivatableQuestion {
    GENERATED_BODY()

public:
    virtual void NativeOnActivated() override {
        Super::NativeOnActivated();
        // Menu activated (shown)
    }

    virtual void NativeOnDeactivated() override {
        Super::NativeOnDeactivated();
        // Menu deactivated (hidden)
    }
};
```

---

## HUD Class (Alternative to UMG)

### Create HUD

```cpp
UCLASS()
class AMyHUD : public AHUD {
    GENERATED_BODY()

public:
    virtual void DrawHUD() override {
        Super::DrawHUD();

        // Draw text
        DrawText(TEXT("Score: 100"), FLinearColor::White, 50, 50);

        // Draw texture
        DrawTexture(CrosshairTexture, Canvas->SizeX / 2, Canvas->SizeY / 2, 32, 32);
    }
};
```

---

## Performance Tips

### Optimize UMG

```cpp
// Invalidation boxes: Only redraw when content changes
// Add "Invalidation Box" question to Question Blueprint

// Disable tick if not needed
bIsFocusable = false;
SetVisibility(ESlateVisibility::Collapsed); // Collapsed = not rendered
```

---

## Debugging

### UI Debug Commands

```cpp
// Console commands:
// question.debug - Show question hierarchy
// Slate.ShowDebugOutlines 1 - Show question bounds
// stat slate - Show Slate performance
```

---

## Sources
- https://docs.unrealengine.com/5.7/en-US/umg-ui-designer-for-unreal-engine/
- https://docs.unrealengine.com/5.7/en-US/commonui-plugin-for-advanced-user-interfaces-in-unreal-engine/
