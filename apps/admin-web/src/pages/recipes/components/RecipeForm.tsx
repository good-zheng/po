import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import {
  ProForm,
  ProFormDigit,
  ProFormRadio,
  ProFormSelect,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { useQuery } from '@tanstack/react-query';
import { Button, Divider, Form, Space } from 'antd';
import { useMemo } from 'react';
import {
  getRecipeCategories,
  type Recipe,
  type RecipeRequest,
} from '@/services/recipe';

type RecipeFormProps = {
  initialValues: Partial<RecipeRequest>;
  submitting: boolean;
  onSubmit: (values: RecipeRequest) => Promise<void>;
};

const difficultyOptions = [
  { label: '简单', value: 1 },
  { label: '中等', value: 2 },
  { label: '困难', value: 3 },
];

export function buildRecipeInitialValues(
  recipe?: Recipe,
): Partial<RecipeRequest> {
  if (!recipe) {
    return {
      difficulty: 1,
      isPublic: true,
      ingredients: [
        { name: '', amount: '', unit: '', isEssential: true, sortOrder: 0 },
      ],
      steps: [{ stepNumber: 1, content: '' }],
    };
  }
  return {
    title: recipe.title,
    description: recipe.description ?? '',
    category: recipe.category ?? '',
    difficulty: recipe.difficulty,
    prepTime: recipe.prepTime ?? undefined,
    cookTime: recipe.cookTime ?? undefined,
    servings: recipe.servings ?? undefined,
    isPublic: recipe.isPublic,
    tags: recipe.tags ?? '',
    tips: recipe.tips ?? '',
    calories: recipe.calories ?? undefined,
    protein: recipe.protein ?? undefined,
    fat: recipe.fat ?? undefined,
    carbs: recipe.carbs ?? undefined,
    flavorProfile: recipe.flavorProfile ?? '',
    coverImageUrl: recipe.coverImageUrl ?? '',
    ingredients: (recipe.ingredients ?? []).map((i) => ({
      name: i.name,
      amount: i.amount ?? undefined,
      unit: i.unit ?? undefined,
      isEssential: i.isEssential ?? true,
      sortOrder: i.sortOrder ?? 0,
    })),
    steps: (recipe.steps ?? []).map((s) => ({
      stepNumber: s.stepNumber,
      content: s.content,
      imageUrl: s.imageUrl ?? undefined,
      videoUrl: s.videoUrl ?? undefined,
      duration: s.duration ?? undefined,
    })),
  };
}

const RecipeForm: React.FC<RecipeFormProps> = ({
  initialValues,
  submitting,
  onSubmit,
}) => {
  const [form] = Form.useForm<RecipeRequest>();

  const { data: categoriesRes } = useQuery({
    queryKey: ['recipe-categories'],
    queryFn: getRecipeCategories,
    staleTime: 5 * 60 * 1000,
  });

  const categories = useMemo(
    () =>
      categoriesRes?.data?.map((c) => ({
        label: c.icon ? `${c.icon} ${c.name}` : c.name,
        value: c.name,
      })) ?? [],
    [categoriesRes],
  );

  return (
    <ProForm<RecipeRequest>
      form={form}
      layout="vertical"
      initialValues={initialValues}
      submitter={false}
      onFinish={async (values) => {
        await onSubmit(values);
        return true;
      }}
    >
      {/* ── 基本信息 ────────────────────────────────────── */}
      <Divider plain titlePlacement="left">
        基本信息
      </Divider>
      <ProFormText
        name="title"
        label="菜谱名称"
        placeholder="请输入菜谱名称"
        rules={[{ required: true, message: '请输入菜谱名称' }]}
      />
      <ProFormTextArea
        name="description"
        label="描述"
        placeholder="请输入菜谱描述"
        fieldProps={{ rows: 3 }}
      />
      <div style={{ display: 'flex', gap: 16 }}>
        <ProFormSelect
          name="category"
          label="分类"
          placeholder="请选择分类"
          options={categories}
          style={{ flex: 1 }}
          allowClear
        />
        <ProFormSelect
          name="difficulty"
          label="难度"
          options={difficultyOptions}
          rules={[{ required: true, message: '请选择难度' }]}
          style={{ flex: 1 }}
        />
      </div>
      <div style={{ display: 'flex', gap: 16 }}>
        <ProFormDigit
          name="servings"
          label="份数"
          placeholder="建议份数"
          min={1}
          style={{ flex: 1 }}
        />
        <ProFormDigit
          name="prepTime"
          label="准备时间(分钟)"
          placeholder="准备时间"
          min={0}
          style={{ flex: 1 }}
        />
        <ProFormDigit
          name="cookTime"
          label="烹饪时间(分钟)"
          placeholder="烹饪时间"
          min={0}
          style={{ flex: 1 }}
        />
      </div>
      <ProFormRadio.Group
        name="isPublic"
        label="公开状态"
        options={[
          { label: '公开', value: true },
          { label: '私密', value: false },
        ]}
      />
      <ProFormText
        name="tags"
        label="标签"
        placeholder="逗号分隔，如：家常菜,快手菜"
      />
      <ProFormText
        name="flavorProfile"
        label="口味"
        placeholder="如：香辣、清淡、酸甜"
      />
      <ProFormText
        name="coverImageUrl"
        label="封面图 URL"
        placeholder="图片链接"
      />

      {/* ── 营养信息 ────────────────────────────────────── */}
      <Divider plain titlePlacement="left">
        营养信息（可选）
      </Divider>
      <div style={{ display: 'flex', gap: 16 }}>
        <ProFormDigit
          name="calories"
          label="热量(kcal)"
          min={0}
          style={{ flex: 1 }}
        />
        <ProFormDigit
          name="protein"
          label="蛋白质(g)"
          min={0}
          step={0.1}
          style={{ flex: 1 }}
        />
        <ProFormDigit
          name="fat"
          label="脂肪(g)"
          min={0}
          step={0.1}
          style={{ flex: 1 }}
        />
        <ProFormDigit
          name="carbs"
          label="碳水(g)"
          min={0}
          step={0.1}
          style={{ flex: 1 }}
        />
      </div>

      <ProFormTextArea
        name="tips"
        label="小贴士"
        placeholder="烹饪小贴士"
        fieldProps={{ rows: 3 }}
      />

      {/* ── 食材列表 ────────────────────────────────────── */}
      <Divider plain titlePlacement="left">
        食材
      </Divider>
      <Form.List name="ingredients">
        {(fields, { add, remove }) => (
          <>
            {fields.map(({ key, name, ...restField }) => (
              <div
                key={key}
                style={{
                  display: 'flex',
                  gap: 8,
                  marginBottom: 8,
                  alignItems: 'flex-start',
                }}
              >
                <Form.Item
                  {...restField}
                  name={[name, 'name']}
                  rules={[{ required: true, message: '食材名称不能为空' }]}
                  style={{ flex: 2, marginBottom: 0 }}
                >
                  <input
                    placeholder="食材名称"
                    style={{
                      width: '100%',
                      padding: '4px 11px',
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                    }}
                  />
                </Form.Item>
                <Form.Item
                  {...restField}
                  name={[name, 'amount']}
                  style={{ flex: 1, marginBottom: 0 }}
                >
                  <input
                    placeholder="用量"
                    style={{
                      width: '100%',
                      padding: '4px 11px',
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                    }}
                  />
                </Form.Item>
                <Form.Item
                  {...restField}
                  name={[name, 'unit']}
                  style={{ flex: 1, marginBottom: 0 }}
                >
                  <input
                    placeholder="单位"
                    style={{
                      width: '100%',
                      padding: '4px 11px',
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                    }}
                  />
                </Form.Item>
                <MinusCircleOutlined
                  onClick={() => remove(name)}
                  style={{ marginTop: 8, color: '#ff4d4f' }}
                />
              </div>
            ))}
            <Button
              type="dashed"
              onClick={() =>
                add({
                  name: '',
                  amount: '',
                  unit: '',
                  isEssential: true,
                  sortOrder: fields.length,
                })
              }
              block
              icon={<PlusOutlined />}
            >
              添加食材
            </Button>
          </>
        )}
      </Form.List>

      {/* ── 步骤列表 ────────────────────────────────────── */}
      <Divider plain titlePlacement="left">
        步骤
      </Divider>
      <Form.List name="steps">
        {(fields, { add, remove }) => (
          <>
            {fields.map(({ key, name, ...restField }) => (
              <div
                key={key}
                style={{
                  display: 'flex',
                  gap: 8,
                  marginBottom: 8,
                  alignItems: 'flex-start',
                }}
              >
                <span
                  style={{
                    minWidth: 24,
                    textAlign: 'center',
                    lineHeight: '32px',
                  }}
                >
                  {name + 1}
                </span>
                <Form.Item
                  {...restField}
                  name={[name, 'stepNumber']}
                  initialValue={name + 1}
                  hidden
                >
                  <input />
                </Form.Item>
                <Form.Item
                  {...restField}
                  name={[name, 'content']}
                  rules={[{ required: true, message: '步骤内容不能为空' }]}
                  style={{ flex: 1, marginBottom: 0 }}
                >
                  <textarea
                    placeholder="步骤描述"
                    rows={2}
                    style={{
                      width: '100%',
                      padding: '4px 11px',
                      border: '1px solid #d9d9d9',
                      borderRadius: 6,
                    }}
                  />
                </Form.Item>
                {fields.length > 1 && (
                  <MinusCircleOutlined
                    onClick={() => remove(name)}
                    style={{ marginTop: 8, color: '#ff4d4f' }}
                  />
                )}
              </div>
            ))}
            <Button
              type="dashed"
              onClick={() =>
                add({ stepNumber: fields.length + 1, content: '' })
              }
              block
              icon={<PlusOutlined />}
            >
              添加步骤
            </Button>
          </>
        )}
      </Form.List>

      <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
        <Space style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={() => window.history.back()}>取消</Button>
          <Button
            type="primary"
            loading={submitting}
            onClick={() => form.submit()}
          >
            保存
          </Button>
        </Space>
      </Form.Item>
    </ProForm>
  );
};

export default RecipeForm;
