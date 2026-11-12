# 在一条样本回复里插几种 MOD 写法，看线上的显示规则各怎么处理
import sys
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'E:/aldran_art/底稿/状态栏/大框/发布/试写/普通战斗.txt', encoding='utf-8').read().replace('\r\n', '\n')
lines = src.split('\n')
def ins_after(prefix, new, last=True):
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert idx, prefix
    i = idx[-1] if last else idx[0]
    lines[i + 1:i + 1] = new
# 甲：照骨架写的 §MOD（领地建设 MOD）
ins_after('§见闻｜线索', ['§MOD｜领地建设｜领地甲｜灰雨城旧南门·一级据点', '§MOD｜领地建设｜人口甲｜四十六户，劳力三十', '§MOD｜领地建设｜粮仓甲｜麦三百袋，够吃到霜降月'])
# 乙：自造的记录名
ins_after('§记忆｜已完成', ['§领地｜灰雨城旧南门乙｜人口 46｜粮 300'])
# 丙：角色行里自造一栏（身体部位 MOD）
ins_after('§角色行｜关系因果', ['§角色行｜身体部位｜头丙 完好 ｜ 躯干 轻伤 ｜ 左臂 包扎'], last=False)
# 丁：面板里自造一栏
ins_after('§面板｜委托', ['§面板｜领地｜灰雨城旧南门丁·一级据点｜人口 46'])
# 戊：MOD 模板里的 HTML 原样写出来
ins_after('§见闻｜线索', ['<details class="mod-territory"><summary>领地面板戊</summary><div class="mod-row"><b>人口</b><span>四十六户戊</span></div><div class="mod-row"><b>粮仓</b><span>麦三百袋</span></div></details>'])
# 己：写成 Markdown 小节
ins_after('§记忆｜已完成', ['', '**【领地面板己】**', '- 人口：四十六户己', '- 粮仓：麦三百袋'])
open(sys.argv[1], 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('ok')
