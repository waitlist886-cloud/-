export default async ({ page, shot, scrollTo }) => {
  await scrollTo('.rili-markdown-renderer', 'start', '0', 70); await shot('1top');
  await scrollTo('.choices', 'center', '0'); await shot('2mid');
};
