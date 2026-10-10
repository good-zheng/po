import { memo } from 'react';
import { View, Text, Image } from '@tarojs/components';
import type { Recipe } from '@po/types';
import { resolveAssetUrl } from '@/lib/api/client';
import { difficultyLabel, splitTags, totalMinutes } from '@/lib/recipe-utils';
import './recipe-card.scss';

const HEART = '♥';
const HEART_OUTLINE = '♡';
const BOOKMARK = '★';

/**
 * 双列网格卡片（首页 / 分类：大图 + 标题 + 元信息 + 点赞/收藏角标）
 *
 * memo 是有实义的：列表页每翻一次页、每次 loading/输入框状态变化都会重渲染整棵页面，
 * 而 recipes 里的对象是同一批引用，不拦住就是几十张卡片陪着白算一遍。
 */
export const RecipeGridCard = memo(function RecipeGridCard({ recipe }: { recipe: Recipe }) {
  const minutes = totalMinutes(recipe);
  return (
    <View className='grid-card'>
      <View className='grid-cover-wrap'>
        {recipe.coverImageUrl ? (
          <Image
            className='grid-cover'
            src={resolveAssetUrl(recipe.coverImageUrl) || ''}
            mode='aspectFill'
            lazyLoad
          />
        ) : (
          <View className='grid-cover-placeholder'>
            <Text className='grid-cover-emoji'>{'\u{1F37D}\uFE0F'}</Text>
          </View>
        )}
        {recipe.category ? (
          <View className='grid-category-badge'>
            <Text className='grid-category-text'>{recipe.category}</Text>
          </View>
        ) : null}
      </View>
      <View className='grid-info'>
        <Text className='grid-title'>{recipe.title}</Text>
        <View className='grid-meta-row'>
          <Text className='grid-meta'>{'\u21D4'} {difficultyLabel(recipe.difficulty)}</Text>
          {minutes ? <Text className='grid-meta grid-meta-right'>{'\u{1F551}'} {minutes} 分钟</Text> : null}
        </View>
        <View className='grid-meta-row'>
          <View className='grid-like-group'>
            <Text className={`grid-like-icon ${recipe.isLiked ? 'grid-like-active' : ''}`}>
              {recipe.isLiked ? HEART : HEART_OUTLINE}
            </Text>
            <Text className='grid-like-count'>{recipe.likesCount ?? 0}</Text>
          </View>
          {recipe.isFavorited ? <Text className='grid-fav-icon'>{BOOKMARK}</Text> : null}
        </View>
      </View>
    </View>
  );
});

/** 单列信息流卡片（收藏 / 历史：大图 + 标题 + 简介 + 标签） */
export const RecipeFeedCard = memo(function RecipeFeedCard({ recipe }: { recipe: Recipe }) {
  const tags = splitTags(recipe.tags).slice(0, 3);
  const minutes = totalMinutes(recipe);
  return (
    <View className='feed-card'>
      {recipe.coverImageUrl ? (
        <Image
          className='feed-cover'
          src={resolveAssetUrl(recipe.coverImageUrl) || ''}
          mode='aspectFill'
          lazyLoad
        />
      ) : (
        <View className='feed-cover-placeholder'>
          <Text className='grid-cover-emoji'>{'\u{1F37D}\uFE0F'}</Text>
        </View>
      )}
      <View className='feed-body'>
        <View className='feed-title-row'>
          <Text className='feed-title'>{recipe.title}</Text>
          {recipe.category ? (
            <Text className='feed-category'>{recipe.category}</Text>
          ) : null}
        </View>
        {recipe.description ? <Text className='feed-desc'>{recipe.description}</Text> : null}
        <View className='feed-meta-row'>
          {minutes ? <Text className='feed-meta'>{'\u{1F551}'} {minutes} 分钟</Text> : null}
          {recipe.servings ? <Text className='feed-meta'>{recipe.servings} 人份</Text> : null}
          {recipe.likesCount > 0 ? <Text className='feed-meta'>{HEART_OUTLINE} {recipe.likesCount}</Text> : null}
        </View>
        {tags.length ? (
          <View className='feed-tags'>
            {tags.map((tag) => (
              <Text key={tag} className='feed-tag'>{tag}</Text>
            ))}
          </View>
        ) : null}
      </View>
    </View>
  );
});

/** 双列瀑布流：微信不支持 flex-wrap，按行切分为每行 2 张 */
export function RecipeGrid({ recipes, onSelect }: { recipes: Recipe[]; onSelect: (id: number) => void }) {
  const rows: Recipe[][] = [];
  for (let i = 0; i < recipes.length; i += 2) {
    rows.push(recipes.slice(i, i + 2));
  }
  return (
    <View className='recipe-grid'>
      {rows.map((row, index) => (
        <View key={`row-${index}`} className='grid-row'>
          {row.map((recipe) => (
            <View key={recipe.id} className='grid-cell' onClick={() => onSelect(recipe.id)}>
              <RecipeGridCard recipe={recipe} />
            </View>
          ))}
          {row.length === 1 ? <View className='grid-cell grid-cell-empty' /> : null}
        </View>
      ))}
    </View>
  );
}
