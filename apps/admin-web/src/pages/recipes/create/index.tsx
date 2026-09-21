import { PageContainer } from '@ant-design/pro-components';
import { useMutation } from '@tanstack/react-query';
import { history } from '@umijs/max';
import { Card, message } from 'antd';
import { useMemo } from 'react';
import { createRecipe, type RecipeRequest } from '@/services/recipe';
import RecipeForm, { buildRecipeInitialValues } from '../components/RecipeForm';

const RecipeCreate: React.FC = () => {
  const [messageApi, contextHolder] = message.useMessage();

  const createMutation = useMutation({
    mutationFn: (data: RecipeRequest) => createRecipe(data),
    onSuccess: (res) => {
      messageApi.success('菜谱创建成功');
      history.push(`/recipes/detail/${res.data.id}`);
    },
    onError: (err: Error) => {
      messageApi.error(err.message || '创建失败');
    },
  });

  const initialValues = useMemo(() => buildRecipeInitialValues(), []);

  return (
    <>
      {contextHolder}
      <PageContainer title="新建菜谱">
        <Card>
          <RecipeForm
            initialValues={initialValues}
            submitting={createMutation.isPending}
            onSubmit={async (values) => {
              await createMutation.mutateAsync(values);
            }}
          />
        </Card>
      </PageContainer>
    </>
  );
};

export default RecipeCreate;
