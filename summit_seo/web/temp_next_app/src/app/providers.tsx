import { ThemeProvider } from "@/contexts/theme-context";
import { AuthProvider } from "@/contexts/auth-context";
import { FeatureDiscoveryProvider } from "@/contexts/feature-discovery-context";
import { SoundEffectsProvider } from "@/contexts/sound-effects-context";
import { KeyboardShortcutsProvider } from "@/contexts/keyboard-shortcuts-context";
import { ResponsiveProvider } from "@/contexts/responsive-context";
import { UserPreferencesProvider } from "@/contexts/user-preferences-context";
import { ABTestingProvider } from "@/contexts/ab-testing-context";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <FeatureDiscoveryProvider>
          <SoundEffectsProvider>
            <KeyboardShortcutsProvider>
              <ResponsiveProvider>
                <UserPreferencesProvider>
                  <ABTestingProvider>
                    {children}
                  </ABTestingProvider>
                </UserPreferencesProvider>
              </ResponsiveProvider>
            </KeyboardShortcutsProvider>
          </SoundEffectsProvider>
        </FeatureDiscoveryProvider>
      </AuthProvider>
    </ThemeProvider>
  );
} 