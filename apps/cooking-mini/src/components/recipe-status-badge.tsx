import { View, Text } from '@tarojs/components';
import type { RecipeStatus } from '@po/types';
import './recipe-status-badge.scss';

export const statusLabels: Record<RecipeStatus, string> = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已驳回',
};

const statusClass: Record<RecipeStatus, string> = {
  pending: 'badge-pending',
  approved: 'badge-approved',
  rejected: 'badge-rejected',
};

type Props = {
  status?: RecipeStatus;
  rejectReason?: string | null;
};

export function RecipeStatusBadge({ status, rejectReason }: Props) {
  if (!status) {
    return null;
  }
  return (
    <View className='status-badge'>
      <Text className={`status-pill ${statusClass[status]}`}>{statusLabels[status]}</Text>
      {status === 'rejected' && rejectReason ? (
        <Text className='status-reason'>驳回原因：{rejectReason}</Text>
      ) : null}
    </View>
  );
}
