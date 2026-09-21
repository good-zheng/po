import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import { PageContainer } from '@ant-design/pro-components';
import { useQuery } from '@tanstack/react-query';
import { history, useParams } from '@umijs/max';
import {
  Badge,
  Button,
  Card,
  Descriptions,
  Empty,
  Image,
  Result,
  Skeleton,
  Space,
  Tag,
  Typography,
} from 'antd';
import dayjs from 'dayjs';
import { getRecipe, type Ingredient, type Step } from '@/services/recipe';

const difficultyMap: Record<number, { text: string; color: string }> = {
  1: { text: '简单', color: 'green' },
  2: { text: '中等', color: 'orange' },
  3: { text: '困难', color: 'red' },
};

const formatDateTime = (value?: string) =>
  value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-';

const stepNumberStyle: React.CSSProperties = {
  display: 'inline-block',
  width: 24,
  height: 24,
  lineHeight: '24px',
  textAlign: 'center',
  borderRadius: '50%',
  background: '#1677ff',
  color: '#fff',
  fontSize: 12,
  flexShrink: 0,
};

const RecipeDetail: React.FC = () => {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const validId = Number.isFinite(id) && id > 0;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['recipe', id],
    queryFn: () => getRecipe(id),
    enabled: validId,
  });

  const recipe = data?.data;
  const difficulty = recipe ? difficultyMap[recipe.difficulty] : undefined;
  const hasNutrition =
    recipe &&
    [recipe.calories, recipe.protein, recipe.fat, recipe.carbs].some(
      (v) => v !== null && v !== undefined,
    );
  const tagList = recipe?.tags
    ? recipe.tags
        .split(/[,，]/)
        .map((t) => t.trim())
        .filter(Boolean)
    : [];

  let content: React.ReactNode;
  if (!validId) {
    content = (
      <Card>
        <Empty description="无效的菜谱 ID" />
      </Card>
    );
  } else if (isLoading) {
    content = (
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    );
  } else if (isError || !recipe) {
    content = (
      <Result
        status="404"
        title="加载失败"
        subTitle={
          error instanceof Error ? error.message : '菜谱不存在或已被删除'
        }
        extra={
          <a onClick={() => history.push('/recipes/list')}>返回菜谱列表</a>
        }
      />
    );
  } else {
    content = (
      <>
        <Card title="基本信息" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            <div style={{ flex: '0 0 280px' }}>
              {recipe.coverImageUrl ? (
                <Image
                  src={recipe.coverImageUrl}
                  alt={recipe.title}
                  style={{ width: 280, borderRadius: 8, objectFit: 'cover' }}
                />
              ) : (
                <Empty
                  description="暂无封面"
                  style={{
                    width: 280,
                    height: 180,
                    border: '1px dashed #d9d9d9',
                    borderRadius: 8,
                  }}
                />
              )}
            </div>
            <div style={{ flex: 1, minWidth: 320 }}>
              {recipe.description && (
                <Typography.Paragraph
                  type="secondary"
                  style={{ marginBottom: 16 }}
                >
                  {recipe.description}
                </Typography.Paragraph>
              )}
              <Descriptions column={2} size="small">
                <Descriptions.Item label="分类">
                  {recipe.category ?? '-'}
                </Descriptions.Item>
                <Descriptions.Item label="难度">
                  {difficulty ? (
                    <Tag color={difficulty.color}>{difficulty.text}</Tag>
                  ) : (
                    recipe.difficulty
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="准备时间">
                  {recipe.prepTime != null ? `${recipe.prepTime} 分钟` : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="烹饪时间">
                  {recipe.cookTime != null ? `${recipe.cookTime} 分钟` : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="总时间">
                  {recipe.totalTime != null ? `${recipe.totalTime} 分钟` : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="份数">
                  {recipe.servings ?? '-'}
                </Descriptions.Item>
                <Descriptions.Item label="公开状态">
                  <Badge
                    status={recipe.isPublic ? 'success' : 'default'}
                    text={recipe.isPublic ? '公开' : '私密'}
                  />
                </Descriptions.Item>
                <Descriptions.Item label="口味">
                  {recipe.flavorProfile ?? '-'}
                </Descriptions.Item>
                <Descriptions.Item label="标签">
                  <Space size={4} wrap>
                    {tagList.length > 0
                      ? tagList.map((t) => <Tag key={t}>{t}</Tag>)
                      : '-'}
                  </Space>
                </Descriptions.Item>
                <Descriptions.Item label="点赞数">
                  {recipe.likesCount}
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {formatDateTime(recipe.createdAt)}
                </Descriptions.Item>
                <Descriptions.Item label="更新时间">
                  {formatDateTime(recipe.updatedAt)}
                </Descriptions.Item>
              </Descriptions>
            </div>
          </div>
        </Card>

        {hasNutrition && (
          <Card title="营养信息" style={{ marginBottom: 16 }}>
            <Descriptions column={4} size="small">
              <Descriptions.Item label="热量">
                {recipe.calories != null ? `${recipe.calories} kcal` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="蛋白质">
                {recipe.protein != null ? `${recipe.protein} g` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="脂肪">
                {recipe.fat != null ? `${recipe.fat} g` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="碳水">
                {recipe.carbs != null ? `${recipe.carbs} g` : '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        )}

        <Card title="食材" style={{ marginBottom: 16 }}>
          {recipe.ingredients && recipe.ingredients.length > 0 ? (
            <Space orientation="vertical" style={{ width: '100%' }} size={8}>
              {recipe.ingredients.map((item: Ingredient) => (
                <div
                  key={`${item.sortOrder}-${item.name}`}
                  style={{ display: 'flex', gap: 16, alignItems: 'center' }}
                >
                  <Typography.Text strong style={{ minWidth: 140 }}>
                    {item.name}
                  </Typography.Text>
                  <Typography.Text type="secondary">
                    {item.amount ?? ''} {item.unit ?? ''}
                  </Typography.Text>
                  {item.isEssential === false && <Tag>可选</Tag>}
                </div>
              ))}
            </Space>
          ) : (
            <Empty description="暂无食材信息" />
          )}
        </Card>

        <Card title="烹饪步骤" style={{ marginBottom: 16 }}>
          {recipe.steps && recipe.steps.length > 0 ? (
            <Space orientation="vertical" style={{ width: '100%' }} size={16}>
              {[...recipe.steps]
                .sort((a: Step, b: Step) => a.stepNumber - b.stepNumber)
                .map((step: Step) => (
                  <div
                    key={step.stepNumber}
                    style={{
                      display: 'flex',
                      gap: 12,
                      alignItems: 'flex-start',
                    }}
                  >
                    <span style={stepNumberStyle}>{step.stepNumber}</span>
                    <div>
                      <Typography.Paragraph style={{ marginBottom: 4 }}>
                        {step.content}
                      </Typography.Paragraph>
                      {step.duration != null && (
                        <Typography.Text type="secondary">
                          约 {step.duration} 分钟
                        </Typography.Text>
                      )}
                    </div>
                  </div>
                ))}
            </Space>
          ) : (
            <Empty description="暂无步骤信息" />
          )}
        </Card>

        {recipe.tips && (
          <Card title="小贴士">
            <Typography.Paragraph style={{ marginBottom: 0 }}>
              {recipe.tips}
            </Typography.Paragraph>
          </Card>
        )}
      </>
    );
  }

  return (
    <PageContainer
      title={recipe?.title ?? '菜谱详情'}
      extra={[
        <Button
          key="back"
          icon={<ArrowLeftOutlined />}
          onClick={() => history.push('/recipes/list')}
        >
          返回列表
        </Button>,
        <Button
          key="edit"
          type="primary"
          icon={<EditOutlined />}
          disabled={!recipe}
          onClick={() => history.push(`/recipes/edit/${id}`)}
        >
          编辑
        </Button>,
      ]}
    >
      {content}
    </PageContainer>
  );
};

export default RecipeDetail;
