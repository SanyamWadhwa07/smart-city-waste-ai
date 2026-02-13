/**
 * Waste Stream Color Coding System
 * 
 * Global color-coding for waste types across:
 * - Bounding boxes
 * - Charts
 * - Labels
 * - Bins
 * - Badges
 * 
 * Users learn the system instantly through consistent colors.
 */

export const wasteColors = {
  plastic: 'waste-plastic',
  paper: 'waste-paper',
  metal: 'waste-metal',
  organic: 'waste-organic',
  glass: 'waste-glass',
  cardboard: 'waste-cardboard',
  biological: 'waste-organic', // Maps to organic
  biodegradable: 'waste-organic', // Maps to organic
} as const;

export type WasteType = keyof typeof wasteColors;

/**
 * Get tailwind color class for a waste type
 */
export function getWasteColor(type: string | undefined): string {
  if (!type) return 'text-muted-foreground';
  
  const normalized = type.toLowerCase().replace(/[-_\s]/g, '');
  
  // Direct match
  for (const [key, value] of Object.entries(wasteColors)) {
    if (normalized.includes(key)) {
      return value;
    }
  }
  
  // Fallback mappings
  if (normalized.includes('recycle')) return 'waste-plastic';
  if (normalized.includes('hazard')) return 'text-destructive';
  if (normalized.includes('contamination')) return 'text-contamination';
  
  return 'text-muted-foreground';
}

/**
 * Get background color class for waste badges
 */
export function getWasteBg(type: string | undefined): string {
  if (!type) return 'bg-muted';
  
  const normalized = type.toLowerCase().replace(/[-_\s]/g, '');
  
  for (const [key] of Object.entries(wasteColors)) {
    if (normalized.includes(key)) {
      return `bg-waste-${key}`;
    }
  }
  
  if (normalized.includes('recycle')) return 'bg-waste-plastic';
  if (normalized.includes('hazard')) return 'bg-destructive/10 border-destructive/20';
  if (normalized.includes('contamination')) return 'contaminated';
  
  return 'bg-muted';
}

/**
 * Get detection overlay color (for bounding boxes)
 * Returns hex color for canvas drawing
 */
export function getDetectionColor(type: string | undefined, isDark = true): string {
  if (!type) return isDark ? '#9BB4BE' : '#5F6B73';
  
  const normalized = type.toLowerCase().replace(/[-_\s]/g, '');
  
  // Dark mode colors (more luminous)
  const darkColors: Record<string, string> = {
    plastic: '#38BDF8',
    paper: '#60A5FA',
    metal: '#94A3B8',
    organic: '#22C55E',
    glass: '#14B8A6',
    cardboard: '#F59E0B',
    contamination: '#F87171',
  };
  
  // Light mode colors  
  const lightColors: Record<string, string> = {
    plastic: '#00AEEF',
    paper: '#2D9CDB',
    metal: '#64748B',
    organic: '#27AE60',
    glass: '#0D9488',
    cardboard: '#F2A735',
    contamination: '#E5533D',
  };
  
  const colors = isDark ? darkColors : lightColors;
  
  for (const [key, value] of Object.entries(colors)) {
    if (normalized.includes(key)) {
      return value;
    }
  }
  
  // Fallbacks
  if (normalized.includes('recycle')) return colors.plastic;
  if (normalized.includes('biological') || normalized.includes('biodegradable')) return colors.organic;
  if (normalized.includes('hazard')) return colors.contamination;
  
  return isDark ? '#9BB4BE' : '#5F6B73';
}

/**
 * Get semantic state color
 */
export function getStateColor(state: 'success' | 'warning' | 'contamination' | 'info'): string {
  const stateMap = {
    success: 'text-success',
    warning: 'text-warning',
    contamination: 'text-contamination',
    info: 'text-info',
  };
  return stateMap[state];
}

/**
 * Chart color palette (HSL values for recharts)
 */
export const chartColors = {
  primary: 'hsl(var(--chart-1))',
  secondary: 'hsl(var(--chart-2))',
  accent: 'hsl(var(--chart-3))',
  success: 'hsl(var(--chart-4))',
  warning: 'hsl(var(--chart-5))',
} as const;
