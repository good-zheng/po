import type { RecipeStatus } from '@po/types';
import { Text, View } from 'react-native';

import { cn } from '@/lib/utils';

const statusStyles: Record<RecipeStatus, string> = {
  pending: 'bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
  approved:
    'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400',
  rejected: 'bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400',
};

export const statusLabels: Record<RecipeStatus, string> = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已驳回',
};

type RecipeStatusBadgeProps = {
  status?: RecipeStatus;
  rejectReason?: string | null;
};

export function RecipeStatusBadge({
  status,
  rejectReason,
}: RecipeStatusBadgeProps) {
  if (!status) {
    return null;
  }

  return (
    <View className="gap-1">
      <View className="self-start">
        <Text
          className={cn(
            'rounded-full px-2.5 py-1 text-xs font-medium',
            statusStyles[status],
          )}
        >
          {statusLabels[status]}
        </Text>
      </View>
      {status === 'rejected' && rejectReason ? (
        <Text className="text-xs leading-5 text-red-500 dark:text-red-400">
          驳回原因：{rejectReason}
        </Text>
      ) : null}
    </View>
  );
}
