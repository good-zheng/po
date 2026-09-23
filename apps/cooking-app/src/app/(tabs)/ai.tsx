import { Ionicons } from '@expo/vector-icons';
import type { Recipe } from '@po/types';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { RecipeChatCard } from '@/components/recipe-chat-card';
import { askAssistant } from '@/lib/ai/chat';
import { fetchRecipeCategories } from '@/lib/api/recipes';
import { type CookingSession, useCooking } from '@/lib/cooking/cooking-context';
import { categoryKeys } from '@/lib/query-keys';
import { cn } from '@/lib/utils';

type ChatMessage = {
  id: number;
  role: 'user' | 'assistant';
  text: string;
  recipes?: Recipe[];
  suggestions?: string[];
};

const welcomeMessage = (): ChatMessage => ({
  id: nextMessageId(),
  role: 'assistant',
  suggestions: ['今晚吃什么', '推荐几道快手菜', '剁椒鱼头怎么做'],
  text: '我是你的做菜助手。报个菜名，我给你讲清用料和步骤；也可以让我按分类挑几道。想动手做时点「开始做菜」，我一步步带着你，该等的步骤帮你计时。',
});

let messageSeq = 0;

function nextMessageId() {
  messageSeq += 1;

  return messageSeq;
}

export default function AiGuideScreen() {
  const insets = useSafeAreaInsets();
  const listRef = useRef<FlatList<ChatMessage>>(null);
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    welcomeMessage(),
  ]);
  const [input, setInput] = useState('');
  const [pending, setPending] = useState(false);
  const { data: categories } = useQuery({
    queryFn: fetchRecipeCategories,
    queryKey: categoryKeys.list(),
  });
  const { cancelCooking, clearNote, note, session } = useCooking();

  useEffect(() => {
    if (!note) {
      return;
    }

    clearNote();
    const minutes = Math.max(
      1,
      Math.round((Date.now() - note.startedAt) / 60_000),
    );
    setMessages((prev) => [
      ...prev,
      {
        id: nextMessageId(),
        role: 'assistant',
        suggestions: ['今晚吃什么', '推荐几道快手菜'],
        text: `「${note.title}」做好了，一共 ${note.stepCount} 步，用时约 ${minutes} 分钟，趁热吃。还想再做一道吗？`,
      },
    ]);
  }, [clearNote, note]);

  const send = useCallback(
    async (raw: string) => {
      const text = raw.trim();
      if (!text || pending) {
        return;
      }

      setInput('');
      setMessages((prev) => [
        ...prev,
        { id: nextMessageId(), role: 'user', text },
      ]);
      setPending(true);

      try {
        const reply = await askAssistant(text, categories ?? []);
        setMessages((prev) => [
          ...prev,
          {
            id: nextMessageId(),
            recipes: reply.recipes,
            role: 'assistant',
            suggestions: reply.suggestions,
            text: reply.text,
          },
        ]);
      } finally {
        setPending(false);
      }
    },
    [categories, pending],
  );

  const resetChat = () => {
    setMessages([welcomeMessage()]);
    setPending(false);
    setInput('');
  };

  const lastAssistantId = [...messages]
    .reverse()
    .find((message) => message.role === 'assistant')?.id;
  const canSend = input.trim().length > 0 && !pending;

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      className="flex-1 bg-stone-50 dark:bg-stone-950"
    >
      <View
        className="flex-row items-center gap-3 border-b border-stone-100 px-4 pb-3 dark:border-stone-800"
        style={{ paddingTop: insets.top + 10 }}
      >
        <View className="h-10 w-10 items-center justify-center rounded-full bg-brand-600">
          <Ionicons color="#ffffff" name="sparkles" size={18} />
        </View>
        <View className="flex-1">
          <Text className="text-base font-bold text-stone-900 dark:text-stone-50">
            AI 指导
          </Text>
          <Text className="mt-0.5 text-xs text-stone-500 dark:text-stone-400">
            做菜的事都可以问我
          </Text>
        </View>
        <Pressable
          accessibilityLabel="清空对话"
          accessibilityRole="button"
          className="h-9 w-9 items-center justify-center rounded-full active:opacity-60"
          hitSlop={8}
          onPress={resetChat}
        >
          <Ionicons color="#a8a29e" name="trash-outline" size={18} />
        </Pressable>
      </View>

      <FlatList
        contentContainerClassName="px-4 pb-4 pt-4"
        data={messages}
        keyboardShouldPersistTaps="handled"
        keyExtractor={(message) => `${message.role}-${message.id}`}
        ListFooterComponent={pending ? <TypingBubble /> : null}
        onContentSizeChange={() =>
          listRef.current?.scrollToEnd({ animated: true })
        }
        ref={listRef}
        renderItem={({ item }) => (
          <MessageBubble
            message={item}
            onSuggestionPress={(suggestion) => void send(suggestion)}
            showSuggestions={!pending && item.id === lastAssistantId}
          />
        )}
        showsVerticalScrollIndicator={false}
      />

      {session ? (
        <CookingBanner onCancel={cancelCooking} session={session} />
      ) : null}

      <View className="flex-row items-end gap-2 border-t border-stone-100 bg-stone-50 px-4 pb-3 pt-2 dark:border-stone-800 dark:bg-stone-950">
        <TextInput
          className="max-h-28 flex-1 rounded-3xl border border-stone-200 bg-white px-4 py-2.5 text-base text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-50"
          multiline
          onChangeText={setInput}
          onSubmitEditing={() => void send(input)}
          placeholder="问问今天做什么菜"
          placeholderTextColor="#a8a29e"
          returnKeyType="send"
          value={input}
        />
        <Pressable
          accessibilityLabel="发送"
          accessibilityRole="button"
          className={cn(
            'h-11 w-11 items-center justify-center rounded-full',
            canSend
              ? 'bg-brand-600 active:opacity-80'
              : 'bg-stone-300 dark:bg-stone-700',
          )}
          disabled={!canSend}
          onPress={() => void send(input)}
        >
          <Ionicons color="#ffffff" name="arrow-up" size={20} />
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

function MessageBubble({
  message,
  showSuggestions,
  onSuggestionPress,
}: {
  message: ChatMessage;
  showSuggestions: boolean;
  onSuggestionPress: (suggestion: string) => void;
}) {
  const isUser = message.role === 'user';

  return (
    <View className={cn('mb-4', isUser ? 'items-end' : 'items-start')}>
      <View className="flex-row items-start gap-2">
        {isUser ? null : <AssistantAvatar />}
        <View
          className={cn(
            'max-w-[85%] rounded-2xl px-4 py-3',
            isUser
              ? 'rounded-tr-md bg-brand-600'
              : 'rounded-tl-md bg-white shadow-sm dark:bg-stone-900',
          )}
        >
          <Text
            className={cn(
              'text-sm leading-6',
              isUser ? 'text-white' : 'text-stone-800 dark:text-stone-100',
            )}
          >
            {message.text}
          </Text>
        </View>
      </View>

      {message.recipes?.length ? (
        <View className="mt-2 w-full pl-10">
          <FlatList
            contentContainerClassName="gap-3 pr-2"
            data={message.recipes}
            horizontal
            keyExtractor={(recipe) => `${message.id}-${recipe.id}`}
            renderItem={({ item }) => <RecipeChatCard recipe={item} />}
            showsHorizontalScrollIndicator={false}
          />
        </View>
      ) : null}

      {showSuggestions && message.suggestions?.length ? (
        <View className="mt-2 flex-row flex-wrap gap-2 pl-10">
          {message.suggestions.map((suggestion) => (
            <Pressable
              className="rounded-full border border-brand-100 bg-white px-3.5 py-2 active:opacity-70 dark:border-stone-700 dark:bg-stone-900"
              key={suggestion}
              onPress={() => onSuggestionPress(suggestion)}
            >
              <Text className="text-xs font-medium text-brand-700 dark:text-brand-500">
                {suggestion}
              </Text>
            </Pressable>
          ))}
        </View>
      ) : null}
    </View>
  );
}

function AssistantAvatar() {
  return (
    <View className="h-8 w-8 items-center justify-center rounded-full bg-brand-50 dark:bg-stone-800">
      <Ionicons color="#ea580c" name="sparkles" size={15} />
    </View>
  );
}

function TypingBubble() {
  return (
    <View className="mb-4 flex-row items-center gap-2">
      <AssistantAvatar />
      <View className="flex-row items-center gap-2 rounded-2xl rounded-tl-md bg-white px-4 py-3 shadow-sm dark:bg-stone-900">
        <ActivityIndicator color="#ea580c" size="small" />
        <Text className="text-sm text-stone-500 dark:text-stone-400">
          正在翻菜谱…
        </Text>
      </View>
    </View>
  );
}

function CookingBanner({
  session,
  onCancel,
}: {
  session: CookingSession;
  onCancel: () => void;
}) {
  return (
    <View className="mx-4 mb-2 flex-row items-center gap-2 rounded-2xl bg-brand-50 px-2 dark:bg-stone-900">
      <Link
        asChild
        href={{ pathname: '/cook/[id]', params: { id: session.recipeId } }}
      >
        <Pressable className="flex-1 flex-row items-center gap-3 rounded-2xl px-2 py-3 active:opacity-80">
          <View className="h-9 w-9 items-center justify-center rounded-full bg-brand-600">
            <Ionicons color="#ffffff" name="flame" size={16} />
          </View>
          <View className="flex-1">
            <Text
              className="text-sm font-semibold text-brand-700 dark:text-brand-500"
              numberOfLines={1}
            >
              正在做「{session.title}」
            </Text>
            <Text className="mt-0.5 text-xs text-stone-500 dark:text-stone-400">
              第 {session.stepIndex + 1}/{session.stepCount} 步 · 点这里继续
            </Text>
          </View>
          <Ionicons color="#ea580c" name="chevron-forward" size={16} />
        </Pressable>
      </Link>
      <Pressable
        accessibilityLabel="结束做菜"
        accessibilityRole="button"
        className="h-9 w-9 items-center justify-center rounded-full active:opacity-60"
        hitSlop={8}
        onPress={onCancel}
      >
        <Ionicons color="#a8a29e" name="close" size={18} />
      </Pressable>
    </View>
  );
}
