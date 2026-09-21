import { PageContainer } from '@ant-design/pro-components';
import { useMutation, useQuery } from '@tanstack/react-query';
import { history, useParams } from '@umijs/max';
import { Card, Empty, message, Result, Skeleton } from 'antd';
import { useMemo } from 'react';
import { getRecipe, type RecipeRequest, updateRecipe } from '@/services/recipe';
import RecipeForm, { buildRecipeInitialValues } from '../components/RecipeForm';

const RecipeEdit: React.FC = () => {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const validId = Number.isFinite(id) && id > 0;
  const [messageApi, contextHolder] = message.useMessage();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['recipe', id],
    queryFn: () => getRecipe(id),
    enabled: validId,
  });

  const updateMutation = useMutation({
    mutationFn: (data: RecipeRequest) => updateRecipe(id, data),
    onSuccess: () => {
      messageApi.success('菜谱更新成功');
      history.push(`/recipes/detail/${id}`);
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '更新失败');
    },
  });

  const initialValues = useMemo(
    () => buildRecipeInitialValues(data?.data),
    [data],
  );

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
  } else if (isError || !data?.data) {
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
      <Card>
        <RecipeForm
          key={id}
          initialValues={initialValues}
          submitting={updateMutation.isPending}
          onSubmit={async (values) => {
            await updateMutation.mutateAsync(values);
          }}
        />
      </Card>
    );
  }

  return (
    <>
      {contextHolder}
      <PageContainer title="编辑菜谱">{content}</PageContainer>
    </>
  );
};

export default RecipeEdit;
