import { PageContainer } from '@ant-design/pro-components';
import { useSearchParams } from '@umijs/max';
import { Alert, Button, Space } from 'antd';
import FindingTable from '../components/FindingTable';

/**
 * 全站冲突台账：默认跨书看所有待裁定的冲突，`?bookId=` 收窄到一本书。
 *
 * 深链是创作台中栏「去冲突台账裁定」的落点：作者刚从某一章撞见冲突，到了这里
 * 还要再选一次作品就把上下文丢掉了（§10.6）。
 *
 * 作者在这里的每一次裁定都会留 basis + decidedBy，台账因此是「谁在什么时候认定了什么」
 * 的审计面，而不只是一个待办清单。
 */
const NovelReviewList: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const rawBookId = Number(searchParams.get('bookId'));
  const bookId =
    Number.isFinite(rawBookId) && rawBookId > 0 ? rawBookId : undefined;

  return (
    <PageContainer title="冲突台账">
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message="裁定语义"
        description={
          <Space direction="vertical" size={4}>
            <span>
              采纳＝以作者身份写下设定条目并关闭旧条目的生效区间；驳回＝这条冲突不成立；
              豁免＝成立但这一章不改（留痕）；打回＝章节退回草稿按修补指令重写。
            </span>
            {bookId != null && (
              <span>
                正在只看 #{bookId} 这本书的冲突。
                <Button
                  type="link"
                  size="small"
                  onClick={() => setSearchParams({})}
                >
                  看全部作品
                </Button>
              </span>
            )}
          </Space>
        }
      />
      <FindingTable bookId={bookId} />
    </PageContainer>
  );
};

export default NovelReviewList;
