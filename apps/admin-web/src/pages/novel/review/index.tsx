import { PageContainer } from '@ant-design/pro-components';
import { Alert } from 'antd';
import FindingTable from '../components/FindingTable';

/**
 * 全站冲突台账：跨书籍看所有待裁定的冲突。
 *
 * 作者在这里的每一次裁定都会留 basis + decidedBy，台账因此是「谁在什么时候认定了什么」
 * 的审计面，而不只是一个待办清单（§10.6）。
 */
const NovelReviewList: React.FC = () => (
  <PageContainer title="冲突台账">
    <Alert
      type="info"
      showIcon
      style={{ marginBottom: 16 }}
      message="裁定语义"
      description={
        <span>
          采纳＝以作者身份写下设定条目并关闭旧条目的生效区间；驳回＝这条冲突不成立；
          豁免＝成立但这一章不改（留痕）；打回＝章节退回草稿按修补指令重写。
        </span>
      }
    />
    <FindingTable />
  </PageContainer>
);

export default NovelReviewList;
