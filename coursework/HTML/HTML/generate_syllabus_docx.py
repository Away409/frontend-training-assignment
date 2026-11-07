from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


OUTPUT = "《前端开发实训》32课时课程教学大纲（修订完善版）.docx"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=80, bottom=80, end=80):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def set_cell_text_style(cell, size=9, bold=False, color="000000", align=None):
    for paragraph in cell.paragraphs:
        if align is not None:
            paragraph.alignment = align
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.15
        for run in paragraph.runs:
            run.font.name = "宋体"
            run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            run.font.size = Pt(size)
            run.bold = bold
            run.font.color.rgb = RGBColor.from_string(color)


def set_table_borders(table, color="9EADBA", size=6):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_col_widths(table, widths):
    table.autofit = False
    for row in table.rows:
        for idx, width in enumerate(widths):
            if idx < len(row.cells):
                row.cells[idx].width = Cm(width)


def add_table(doc, headers, rows, widths=None, font_size=9, center_cols=None):
    center_cols = set(center_cols or [])
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    set_table_borders(table)
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, header in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = str(header)
        set_cell_shading(cell, "D9EAF2")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(cell)
        set_cell_text_style(cell, size=font_size, bold=True, color="17365D", align=WD_ALIGN_PARAGRAPH.CENTER)
    for r_idx, values in enumerate(rows):
        row = table.add_row()
        prevent_row_split(row)
        if r_idx % 2 == 1:
            for cell in row.cells:
                set_cell_shading(cell, "F7FAFC")
        for i, value in enumerate(values):
            cell = row.cells[i]
            cell.text = str(value)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            align = WD_ALIGN_PARAGRAPH.CENTER if i in center_cols else WD_ALIGN_PARAGRAPH.LEFT
            set_cell_text_style(cell, size=font_size, align=align)
    if widths:
        set_col_widths(table, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.left_indent = Cm(0.74 + 0.5 * level)
    p.paragraph_format.first_line_indent = Cm(-0.38)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.4
    run = p.add_run(text)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(10.5)
    return p


def add_numbered(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Cm(0.74)
    p.paragraph_format.first_line_indent = Cm(-0.38)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.4
    run = p.add_run(text)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(10.5)
    return p


def add_body(doc, text, bold_prefix=None, center=False, indent=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(5)
    if indent and not center:
        p.paragraph_format.first_line_indent = Cm(0.74)
    if bold_prefix and text.startswith(bold_prefix):
        r1 = p.add_run(bold_prefix)
        r1.bold = True
        r2 = p.add_run(text[len(bold_prefix):])
        runs = (r1, r2)
    else:
        runs = (p.add_run(text),)
    for run in runs:
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = Pt(10.5)
    return p


def add_toc(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("目　录")
    run.bold = True
    run.font.name = "黑体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    run.font.size = Pt(18)
    p.paragraph_format.space_after = Pt(18)

    toc_p = doc.add_paragraph()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "在Word中右键单击此处，选择“更新域”即可生成目录。"
    fld_sep.append(placeholder)
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    toc_p._p.extend([fld_begin, instr, fld_sep, fld_end])


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_begin, instr, fld_end])


def configure_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(10.5)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(5)

    specs = {
        "Title": ("黑体", 26, RGBColor(23, 54, 93), WD_ALIGN_PARAGRAPH.CENTER, 0, 18),
        "Heading 1": ("黑体", 15, RGBColor(23, 54, 93), WD_ALIGN_PARAGRAPH.LEFT, 12, 6),
        "Heading 2": ("黑体", 12, RGBColor(31, 78, 121), WD_ALIGN_PARAGRAPH.LEFT, 9, 4),
        "Heading 3": ("黑体", 10.5, RGBColor(49, 97, 125), WD_ALIGN_PARAGRAPH.LEFT, 6, 3),
    }
    for name, (font_name, size, color, alignment, before, after) in specs.items():
        style = doc.styles[name]
        style.font.name = font_name
        style._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
        style.font.size = Pt(size)
        style.font.color.rgb = color
        style.font.bold = True
        style.paragraph_format.alignment = alignment
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True


def create_document():
    doc = Document()
    configure_styles(doc)
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.4)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.3)
    section.right_margin = Cm(2.3)
    section.header_distance = Cm(1.2)
    section.footer_distance = Cm(1.2)
    section.different_first_page_header_footer = True

    props = doc.core_properties
    props.title = "《前端开发实训》32课时课程教学大纲"
    props.subject = "软件工程专业实践类课程教学大纲"
    props.author = "课程教学团队"
    props.keywords = "前端开发实训, Vue 3, 课程教学大纲, 软件工程"
    props.comments = "依据32课时项目驱动教学要求修订完善"

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hr = header.add_run("软件工程专业《前端开发实训》课程教学大纲")
    hr.font.name = "宋体"
    hr._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    hr.font.size = Pt(9)
    hr.font.color.rgb = RGBColor(100, 116, 139)
    add_page_number(section.footer.paragraphs[0])
    section.first_page_header.paragraphs[0].text = ""
    section.first_page_footer.paragraphs[0].text = ""

    # Cover
    for _ in range(4):
        doc.add_paragraph()
    title = doc.add_paragraph(style="Title")
    title.add_run("《前端开发实训》")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = subtitle.add_run("课程教学大纲")
    sr.bold = True
    sr.font.name = "黑体"
    sr._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    sr.font.size = Pt(24)
    sr.font.color.rgb = RGBColor(23, 54, 93)
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    nr = note.add_run("（32课时·修订完善版）")
    nr.font.name = "楷体"
    nr._element.rPr.rFonts.set(qn("w:eastAsia"), "楷体")
    nr.font.size = Pt(14)
    nr.font.color.rgb = RGBColor(49, 97, 125)

    doc.add_paragraph().paragraph_format.space_after = Pt(36)
    cover_rows = [
        ("课程性质", "软件工程专业实践类必修课"),
        ("适用专业", "软件工程、计算机科学与技术及相关专业"),
        ("适用年级", "大学二年级"),
        ("总学时／学分", "32课时／建议2学分（以学校规定为准）"),
        ("开课单位", "____________________________"),
        ("课程负责人", "____________________________"),
        ("审核人", "____________________________"),
    ]
    cover_table = add_table(doc, ["项目", "内容"], cover_rows, widths=[4.5, 10.5], font_size=11)
    for row in cover_table.rows:
        row.height = Cm(0.8)
    date = doc.add_paragraph()
    date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date.paragraph_format.space_before = Pt(22)
    dr = date.add_run("编制日期：2026年7月")
    dr.font.name = "宋体"
    dr._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    dr.font.size = Pt(11)

    doc.add_page_break()
    add_toc(doc)
    doc.add_page_break()

    # 1
    doc.add_heading("一、课程基本信息", level=1)
    basic_rows = [
        ("课程名称", "前端开发实训", "英文名称", "Front-end Development Practice"),
        ("课程代码", "由学校统一编制", "课程性质", "专业实践类必修课"),
        ("适用专业", "软件工程及相关专业", "建议学期", "第四学期"),
        ("总学时", "32课时", "建议学分", "2学分（以学校规定为准）"),
        ("理论学时", "8课时", "实践学时", "24课时"),
        ("实践构成", "教师示范与指导6课时；学生独立或协作实践18课时", "考核方式", "考查：过程考核＋综合项目＋答辩"),
        ("先修课程", "程序设计基础、Web前端基础、JavaScript程序设计", "后续课程", "Web应用开发、软件工程综合实践、毕业设计"),
        ("建议规模", "30～40人；项目组3～4人", "教学组织", "16次课，每次2课时"),
    ]
    add_table(doc, ["项目", "内容", "项目", "内容"], basic_rows, widths=[2.4, 5.8, 2.4, 5.8], font_size=9.5, center_cols=[0, 2])
    add_body(doc, "说明：本课程每课时按45分钟计算，每次课90分钟。实践学时24课时中包含教师示范与指导6课时、学生独立或协作实践18课时。若学校采用其他学分或课时折算办法，以本校教学管理规定为准。")

    # 2
    doc.add_heading("二、课程性质、定位与任务", level=1)
    add_body(doc, "《前端开发实训》是软件工程专业面向大学二年级学生开设的项目驱动型实践课程。课程以学生已经掌握的HTML、CSS和JavaScript基础知识为起点，以“完成一个可运行、可维护、可测试、可部署的现代前端应用”为主线，将零散的知识整合为完整的前端工程实践能力。")
    add_body(doc, "课程不以记忆框架API为主要目标，而是引导学生经历需求理解、界面设计、组件划分、编码实现、接口联调、缺陷调试、协作开发、构建部署和项目复盘的完整过程，使学生初步形成软件工程意识、用户意识、质量意识、安全意识和团队协作意识。")
    add_body(doc, "本大纲适用于已完成HTML、CSS和JavaScript基础学习的学生。对于未达到先修要求的班级，应在开课前安排JavaScript预备学习和诊断测试，并适当减少状态管理、自动化测试等提高性内容。")

    # 3
    doc.add_heading("三、课程教学目标", level=1)
    objectives = [
        "课程目标1（界面实现）：能够根据需求说明、页面原型或设计稿，使用语义化HTML和现代CSS完成结构合理、视觉清晰、具备基本可访问性和响应式能力的页面。",
        "课程目标2（交互与组件化）：能够使用JavaScript ES6+和Vue 3组合式API完成数据处理、页面交互、表单校验和组件化开发，并遵循单向数据流和组件职责清晰的原则。",
        "课程目标3（应用集成）：能够使用前端路由、状态管理和统一请求模块构建中小型单页应用，能够阅读REST风格接口文档并处理加载、空数据、失败和重复提交等状态。",
        "课程目标4（工程质量）：能够使用Vite、Git、浏览器开发者工具、代码规范工具等完成依赖管理、版本控制、调试、基本测试、生产构建和静态部署，具备初步的性能与安全意识。",
        "课程目标5（协作与发展）：能够在小组中完成任务分工、分支协作、代码审查、文档编写和项目汇报；能够查阅官方文档、分析错误信息、合理使用生成式人工智能并对技术结果负责。",
    ]
    for item in objectives:
        add_numbered(doc, item)

    # 4
    doc.add_heading("四、课程目标与毕业要求的对应关系", level=1)
    add_body(doc, "下表采用工程教育的一般毕业要求类别进行建议性映射。正式备案时，应根据本校软件工程专业培养方案，将其替换为本专业正式的毕业要求编号和指标点。")
    mapping_rows = [
        ("1", "工程知识；设计／开发解决方案", "运用Web标准和前端基础知识设计并实现用户界面", "高"),
        ("2", "问题分析；设计／开发解决方案", "分析交互逻辑和数据关系，采用组件化方法实现功能", "高"),
        ("3", "设计／开发解决方案；现代工具", "根据接口规范完成路由、状态和数据交互", "高"),
        ("4", "现代工具；工程与社会", "使用开发、调试、测试、构建和部署工具保障质量", "高"),
        ("5", "个人与团队；沟通；终身学习；职业规范", "开展协作、表达、自主学习并遵守诚信与安全规范", "中"),
    ]
    add_table(doc, ["课程目标", "建议对应的毕业要求类别", "支撑内容", "支撑强度"], mapping_rows, widths=[2.0, 4.6, 7.6, 1.6], font_size=9, center_cols=[0, 3])

    # 5
    doc.add_heading("五、教学理念与教学原则", level=1)
    principles = [
        ("项目贯穿", "围绕一个真实、可交付的前端应用组织32课时，每次课形成可验收的项目增量。"),
        ("学生中心", "采用“问题导入—精讲示范—学生编码—检查反馈—总结迁移”的课堂流程，保证学生实践时间。"),
        ("能力导向", "考查需求理解、问题分析、代码实现、调试验证、协作交付和技术表达，不以API记忆为主要评价依据。"),
        ("工程规范", "同时评价功能、代码结构、版本记录、异常处理、用户体验、测试、文档和部署质量。"),
        ("基础与工具并重", "既学习Vue 3等现代工具，也理解DOM事件、响应式数据、组件数据流、HTTP请求、路由和构建的基本原理。"),
        ("分层发展", "必做任务保障基本达成，选做任务鼓励综合应用，拓展任务支持能力较强的学生继续探索。"),
    ]
    add_table(doc, ["原则", "实施要求"], principles, widths=[3.0, 13.0], font_size=9.5, center_cols=[0])

    # 6
    doc.add_heading("六、教学重点与难点", level=1)
    doc.add_heading("（一）教学重点", level=2)
    for text in [
        "语义化页面结构、响应式布局和基本可访问性；",
        "JavaScript模块化、数组数据处理、异步编程和错误处理；",
        "Vue 3响应式数据、组件化开发和组件通信；",
        "前端路由、合理的状态范围和统一接口请求模块；",
        "Git版本控制、调试、测试、构建、部署和工程规范。",
    ]:
        add_bullet(doc, text)
    doc.add_heading("（二）教学难点", level=2)
    for text in [
        "将业务需求转化为页面结构、组件结构和数据模型；",
        "正确划分组件职责，避免组件过大、过度拆分或数据流混乱；",
        "区分局部状态、父子共享状态和跨页面全局状态，避免滥用状态管理工具；",
        "处理异步请求中的加载、空数据、失败、取消和重复提交等边界状态；",
        "在跨组件、跨模块场景中定位缺陷，并通过测试或回归步骤验证修复结果；",
        "在功能范围、交付进度、代码质量和用户体验之间作出合理权衡。",
    ]:
        add_bullet(doc, text)

    # 7
    doc.add_heading("七、贯穿式实训项目设计", level=1)
    doc.add_heading("（一）推荐项目", level=2)
    add_body(doc, "推荐项目为“校园活动管理平台前端”。系统面向普通学生，提供活动浏览、查询、详情查看、报名、收藏和个人信息查看等功能。教师提供页面原型、静态JSON数据、Mock接口或简单后端服务。也可根据专业方向替换为任务管理、图书借阅、设备预约、在线学习或校园二手交易等同等规模项目。")
    doc.add_heading("（二）项目组织", level=2)
    add_bullet(doc, "建议3～4人组成一个项目组，每名学生独立负责至少一个完整业务功能，并能够在答辩中解释本人提交的代码。")
    add_bullet(doc, "采用个人项目时，应缩减功能范围，只要求完成必做功能中的5～7项，不强制实现用户状态、个人中心和全局状态持久化。")
    add_bullet(doc, "小组应使用任务看板、Git分支和合并记录保存真实开发过程，不以代码提交行数作为个人贡献的唯一依据。")
    doc.add_heading("（三）功能分级", level=2)
    project_rows = [
        ("必做（Must）", "活动列表；搜索或分类筛选；活动详情；报名表单与校验；路由导航；加载／空数据／错误状态；响应式布局；生产构建与部署"),
        ("选做（Should）", "收藏管理；个人中心；用户状态模拟；Pinia持久化；404页面；分页或无限滚动"),
        ("拓展（Could）", "TypeScript类型约束；自动化测试；数据可视化；深色模式；多语言；PWA；真实后端登录与权限联调"),
    ]
    add_table(doc, ["层级", "功能范围"], project_rows, widths=[3.2, 12.8], font_size=9.5, center_cols=[0])
    doc.add_heading("（四）最低质量要求", level=2)
    for text in [
        "项目能够通过统一命令安装、运行和构建，不出现阻断核心流程的严重错误；",
        "页面结构清晰，在常见桌面端和移动端宽度下可用；",
        "公共组件具备合理复用性，组件职责和数据流清晰；",
        "对加载、空数据、失败和表单提交状态提供明确反馈；",
        "不在代码和仓库中明文保存真实账号、密码、访问令牌或密钥；",
        "Git记录能够反映真实开发过程，README包含运行方法、功能说明、成员分工、项目截图和已知问题。",
    ]:
        add_bullet(doc, text)

    # 8 schedule
    doc.add_heading("八、32课时教学内容与进度安排", level=1)
    add_body(doc, "课程按16次课组织，每次2课时。每次课原则上包含0.5课时理论讲授和1.5课时实践，共计理论8课时、实践24课时。教师示范与指导时间包含在实践学时内。")
    schedule = [
        (1, "课程导入、环境与Git基础", "课程要求；Node.js、包管理器、Vite、Git；.gitignore；基础提交", "项目成功运行；初始化仓库；完成首次提交", "0.5", "1.5"),
        (2, "需求分析、组件规划与分支规范", "用户故事；验收标准；页面流程；路由表；组件树；分支与提交规范", "需求清单、组件树、任务分工和功能分支", "0.5", "1.5"),
        (3, "语义化HTML与基础样式", "语义标签；表单结构；CSS变量；基础样式组织；可访问性入门", "首页、公共页面骨架和基础样式", "0.5", "1.5"),
        (4, "响应式布局", "Flexbox；Grid；媒体查询；移动优先；图片适配；颜色对比", "导航栏、活动卡片和响应式列表", "0.5", "1.5"),
        (5, "JavaScript数据处理与模块化", "解构；展开；数组高阶方法；ES Module；不可变数据处理", "使用本地数据实现搜索、筛选和排序", "0.5", "1.5"),
        (6, "异步编程、HTTP与请求状态", "Promise；async/await；HTTP；REST；JSON；Axios基础；异常状态", "调用Mock接口；实现加载、空数据、失败和重试", "0.5", "1.5"),
        (7, "Vue 3响应式基础", "单文件组件；组合式API；ref、reactive、computed、watch；模板语法", "将静态列表改造为响应式页面", "0.5", "1.5"),
        (8, "组件化与组件通信", "组件边界；Props；Emits；插槽；单向数据流；复用原则", "抽取导航、卡片、筛选器和状态提示组件", "0.5", "1.5"),
        (9, "表单、校验与交互反馈", "双向绑定；事件；校验规则；提交状态；防重复提交", "完成报名表单、校验和提交反馈", "0.5", "1.5"),
        (10, "路由与页面组织", "Vue Router；动态参数；嵌套路由；导航守卫；404页面", "完成列表、详情、个人中心等页面导航", "0.5", "1.5"),
        (11, "状态范围与Pinia", "局部／共享／全局状态；Store；派生状态；持久化；避免滥用", "实现用户、收藏或报名状态共享", "0.5", "1.5"),
        (12, "API封装与综合联调", "Axios实例；请求模块；环境变量；数据适配；统一错误处理", "封装API层，完成列表、详情和报名联调", "0.5", "1.5"),
        (13, "Git高级协作与代码质量", "合并请求；冲突解决；代码审查；ESLint；Prettier；目录规范", "完成一次合并和同伴代码审查", "0.5", "1.5"),
        (14, "调试、测试用例与缺陷修复", "DevTools；断点；网络面板；边界用例；缺陷记录；回归验证", "提交测试清单，定位并修复至少两个缺陷", "0.5", "1.5"),
        (15, "构建、部署、性能与安全检查", "生产构建；静态部署；路由懒加载；Lighthouse；密钥与XSS风险", "完成在线部署和基本质量检查报告", "0.5", "1.5"),
        (16, "项目验收、答辩与复盘", "项目演示；代码讲解；个人贡献；互评；知识总结；后续路线", "提交最终项目、报告并完成答辩", "0.5", "1.5"),
    ]
    add_table(doc, ["次", "主题", "主要教学内容", "课堂实践与成果", "理论", "实践"], schedule, widths=[0.75, 2.7, 5.4, 5.4, 0.9, 0.9], font_size=8, center_cols=[0, 4, 5])
    total_table = add_table(doc, ["学时类别", "理论讲授", "实践教学", "其中：示范指导", "其中：学生实践", "总学时"], [("学时", "8", "24", "6", "18", "32")], widths=[3.0, 2.6, 2.6, 3.0, 3.0, 2.0], font_size=9.5, center_cols=[0, 1, 2, 3, 4, 5])

    # 9 implementation
    doc.add_heading("九、教学单元实施要求", level=1)
    units = [
        ("单元一：项目启动与工程环境（第1～2次课，4课时）",
         "使学生理解项目交付要求，能够创建并运行现代前端项目，完成需求拆分、组件规划和基础版本管理。",
         "环境版本不一致、依赖安装、.gitignore、用户故事、验收标准、路由表、组件树、分支与提交规范。",
         "提交可运行仓库、需求清单、组件树和分工表。检查项目能否重新安装运行，并抽查提交记录。"),
        ("单元二：页面基础与响应式实现（第3～4次课，4课时）",
         "使学生能够使用语义化HTML、Flexbox、Grid和媒体查询完成可用的响应式页面，并形成基本可访问性意识。",
         "语义标签、表单标签、CSS变量、移动优先、图片适配、键盘访问、替代文本和颜色对比。",
         "提交首页、导航栏、活动列表和移动端截图；检查溢出、表单标签、替代文本和样式复用。"),
        ("单元三：JavaScript数据与异步请求（第5～6次课，4课时）",
         "使学生能够使用数组方法和模块化完成数据处理，能够使用async/await调用接口并处理完整请求状态。",
         "map、filter、find、some、reduce；ES Module；Promise；HTTP状态码；Axios基础；loading、empty、error、success。",
         "提交搜索筛选功能、接口请求页面和异常重试功能；不得只实现请求成功路径。"),
        ("单元四：Vue 3与组件化开发（第7～9次课，6课时）",
         "使学生理解数据驱动视图和单向数据流，能够使用组合式API、Props、Emits和插槽完成组件化页面与表单。",
         "ref、reactive、computed、watch；组件职责；Props与Emits；表单绑定、校验、提交反馈。",
         "提交组件目录、组件关系说明和报名表单；要求学生解释每个组件的职责和数据来源。"),
        ("单元五：路由、状态管理与接口封装（第10～12次课，6课时）",
         "使学生能够构建单页应用，依据状态作用范围选择管理方式，封装请求代码并完成基本联调。",
         "动态路由、导航守卫、404；局部与全局状态；Pinia；Axios实例；环境变量；数据适配和统一错误处理。",
         "提交路由配置、Store和API模块；页面中不得散落大量重复请求代码，不得将所有状态不加区分地放入全局Store。"),
        ("单元六：协作、质量与交付（第13～16次课，8课时）",
         "使学生能够通过代码审查、调试、测试、构建和部署保障项目质量，并完成技术表达和项目复盘。",
         "合并冲突、代码审查、DevTools、测试清单、回归验证、路由懒加载、Lighthouse、敏感信息保护、部署与答辩。",
         "提交审查记录、缺陷记录、在线地址、项目报告和答辩材料；自动化测试作为提高任务，不强制全体学生完成。"),
    ]
    for title, goal, content, evidence in units:
        doc.add_heading(title, level=2)
        add_body(doc, "教学目标：" + goal, bold_prefix="教学目标：")
        add_body(doc, "核心内容：" + content, bold_prefix="核心内容：")
        add_body(doc, "验收证据：" + evidence, bold_prefix="验收证据：")

    # 10 methods
    doc.add_heading("十、教学方法与课堂组织", level=1)
    methods = [
        ("项目驱动", "所有知识点均服务于贯穿项目，通过持续迭代形成完整成果。"),
        ("任务驱动", "每次课公布任务、验收标准和提交要求，并设置基础、提高和挑战三个层次。"),
        ("现场编码", "教师重点展示需求分析、文档检索、错误定位、逐步验证和重构过程。"),
        ("结对编程", "在组件设计、缺陷调试和代码审查环节轮换驾驶员与观察员角色。"),
        ("翻转课堂", "将路由、状态管理和测试的概念性材料安排在课前，课堂用于验证理解和项目实践。"),
        ("代码讲评", "选择具有代表性的匿名代码，从正确性、可读性、复用性和可维护性进行分析。"),
    ]
    add_table(doc, ["教学方法", "实施方式"], methods, widths=[3.0, 13.0], font_size=9.5, center_cols=[0])
    doc.add_heading("建议的单次课时间结构", level=2)
    classroom_rows = [
        ("上次任务反馈与问题导入", "10分钟"),
        ("核心知识精讲", "20分钟"),
        ("教师现场示范", "15分钟"),
        ("学生实践与巡回指导", "35分钟"),
        ("成果检查、讲评与总结", "10分钟"),
        ("合计", "90分钟"),
    ]
    add_table(doc, ["教学环节", "建议时间"], classroom_rows, widths=[11.0, 5.0], font_size=9.5, center_cols=[1])

    # 11 tasks
    doc.add_heading("十一、过程性任务与阶段成果", level=1)
    task_rows = [
        ("T1", "开发环境与项目初始化", "Git仓库、运行截图、README初稿", "第1次课后"),
        ("T2", "需求与组件设计", "功能清单、路由表、组件树、分工表", "第2次课后"),
        ("T3", "响应式页面", "首页、列表页、桌面端与移动端截图", "第4次课后"),
        ("T4", "数据筛选与接口请求", "搜索筛选、请求状态和异常重试", "第6次课后"),
        ("T5", "Vue组件化改造", "组件目录、Props／Emits说明", "第8次课后"),
        ("T6", "报名表单", "校验规则、提交状态和操作反馈", "第9次课后"),
        ("T7", "路由与状态管理", "路由配置、Store和核心页面", "第11次课后"),
        ("T8", "接口综合联调", "API封装、环境配置和异常处理记录", "第12次课后"),
        ("T9", "代码审查与测试", "审查记录、测试清单和缺陷记录", "第14次课后"),
        ("T10", "综合项目交付", "源代码、在线地址、报告和答辩材料", "第16次课"),
    ]
    add_table(doc, ["编号", "任务", "主要提交物", "时间"], task_rows, widths=[1.4, 4.0, 7.8, 2.8], font_size=9, center_cols=[0, 3])

    # 12 assessment
    doc.add_heading("十二、考核方式与成绩评定", level=1)
    add_body(doc, "课程采用过程性评价与终结性评价相结合的方式，突出实践过程、个人贡献和成果可解释性。课程总成绩满分100分。")
    assessment_rows = [
        ("课堂实践与阶段任务", "25%", "任务完成度、代码正确性、提交及时性、课堂参与", "1、2、3"),
        ("Git过程与工程规范", "10%", "提交记录、分支使用、提交信息、目录和代码规范", "4、5"),
        ("阶段检查", "15%", "现场运行、功能解释、组件设计和现场修改", "1、2、3、4"),
        ("团队协作与代码审查", "10%", "任务分工、合并记录、同伴审查、问题沟通", "5"),
        ("综合项目", "30%", "功能、架构、用户体验、数据处理、测试和部署", "1、2、3、4"),
        ("项目答辩与个人陈述", "10%", "技术表达、代码理解、问题回答、个人贡献", "4、5"),
        ("合计", "100%", "", ""),
    ]
    add_table(doc, ["考核项目", "比例", "评价内容", "课程目标"], assessment_rows, widths=[4.1, 1.8, 8.0, 2.1], font_size=9, center_cols=[1, 3])
    add_body(doc, "课堂实践评价“是否按要求完成每次任务”，阶段检查评价“能否现场运行、解释和修改阶段成果”，二者评价证据不同，避免对同一成果重复计分。")

    doc.add_heading("（一）综合项目评分量规", level=2)
    rubric_rows = [
        ("功能完整性", "25", "核心流程完整，边界场景处理合理，无阻断性错误"),
        ("页面与用户体验", "15", "布局清晰，响应式可用，操作反馈明确，具备基本可访问性"),
        ("组件与代码设计", "20", "组件职责清楚，数据流合理，重复代码少，命名可读"),
        ("数据与异常处理", "10", "正确处理加载、空数据、失败、校验和重复提交"),
        ("工程规范", "10", "目录合理，依赖清晰，规范统一，能够稳定构建"),
        ("测试与缺陷修复", "10", "具有有效测试清单和缺陷记录，能够说明验证过程"),
        ("文档与部署", "10", "README完整，运行步骤准确，部署版本可访问"),
        ("合计", "100", ""),
    ]
    add_table(doc, ["评价维度", "分值", "达成要求"], rubric_rows, widths=[4.1, 1.8, 10.1], font_size=9, center_cols=[1])

    doc.add_heading("（二）团队成绩与个人成绩", level=2)
    add_body(doc, "个人综合项目成绩＝团队项目成绩×70%＋个人贡献成绩×30%。")
    add_body(doc, "个人贡献证据包括Git提交记录、任务看板、代码审查记录、开发日志、答辩表现和成员互评。不以代码行数或提交次数作为唯一判断依据。")

    doc.add_heading("（三）基本门槛与诚信要求", level=2)
    for text in [
        "项目无法按说明安装或运行，综合项目成绩原则上最高不超过60分；",
        "学生无法解释本人负责的核心代码，个人综合项目成绩原则上最高不超过60分，并可安排现场补充考核；",
        "无正当理由未参加答辩，答辩成绩记为0分；",
        "确认存在抄袭、伪造Git过程或其他学术不端行为，按照学校学术诚信规定处理；",
        "即使课程总分达到60分，若个人答辩或核心实践未达到基本要求，教师可要求完成补充实践后再认定课程达成情况。",
    ]:
        add_bullet(doc, text)

    # 13 goal attainment
    doc.add_heading("十三、课程目标达成度评价", level=1)
    attainment_rows = [
        ("1", "响应式页面任务、阶段检查、综合项目中的页面与体验评分项", "20%"),
        ("2", "JavaScript数据任务、组件化任务、综合项目中的代码设计评分项", "25%"),
        ("3", "路由状态任务、接口联调、综合项目中的数据处理评分项", "20%"),
        ("4", "Git规范、调试测试、构建部署、综合项目工程评分项", "20%"),
        ("5", "协作记录、同伴审查、文档、答辩和学习复盘", "15%"),
        ("合计", "", "100%"),
    ]
    add_table(doc, ["课程目标", "主要评价证据", "建议权重"], attainment_rows, widths=[2.4, 11.2, 2.4], font_size=9, center_cols=[0, 2])
    add_body(doc, "课程目标i达成度＝Σ（该目标在各考核点上的学生平均得分）÷Σ（该目标在各考核点上的满分）。")
    add_body(doc, "综合项目应按评分项拆分到相应课程目标，不得将综合项目总分同时完整计入多个目标。建议将0.70作为基本达成参考值；学校已有统一规定时，按学校规定执行。")

    # 14 answer presentation
    doc.add_heading("十四、项目验收与答辩要求", level=1)
    answer_rows = [
        ("项目背景与目标", "1分钟"),
        ("主要功能演示", "3分钟"),
        ("组件结构、数据流与接口说明", "2分钟"),
        ("重点技术问题及解决过程", "2分钟"),
        ("团队分工与项目复盘", "1分钟"),
        ("教师提问或现场修改", "2～3分钟"),
    ]
    add_table(doc, ["答辩环节", "建议时间"], answer_rows, widths=[11.0, 5.0], font_size=9.5, center_cols=[1])
    add_body(doc, "重点提问包括：组件为何如此划分；哪些状态需要全局管理；接口失败如何处理；如何防止重复提交；最难定位的缺陷是什么；如何验证修复；如果项目规模扩大，现有结构应如何调整。")

    # 15 environment
    doc.add_heading("十五、实验与实践环境", level=1)
    environment_rows = [
        ("硬件", "每人或每两人一台计算机；内存建议8GB以上；具备投影和网络环境"),
        ("操作系统", "Windows、macOS或Linux"),
        ("运行环境", "开课当学期仍受支持的Node.js长期支持版本（LTS）"),
        ("开发工具", "Visual Studio Code、Chrome或Edge、Git、npm或pnpm"),
        ("核心框架", "Vue 3、Vite、Vue Router、Pinia"),
        ("请求工具", "统一使用Axios；先讲HTTP与异步原理，再讲工程化封装"),
        ("质量工具", "ESLint、Prettier；Vitest作为提高任务"),
        ("接口环境", "Mock数据、Mock服务或课程后端服务"),
        ("拓展技术", "TypeScript、数据可视化、PWA等，不纳入全体学生必修要求"),
    ]
    add_table(doc, ["类别", "配置要求"], environment_rows, widths=[3.2, 12.8], font_size=9.5, center_cols=[0])
    add_body(doc, "教师应在开课前提供软件版本清单、环境安装指南、项目起始模板、接口说明和常见环境问题处理手册。课程目标强调稳定的工程能力，具体工具版本可随行业生态和学校环境调整。")

    # 16 resources
    doc.add_heading("十六、课程资源与参考资料", level=1)
    doc.add_heading("（一）教师提供资源", level=2)
    for text in [
        "课程教学日历、项目需求说明书、页面原型或设计稿；",
        "接口文档、Mock数据、起始代码模板和环境安装指南；",
        "每次课任务书、阶段验收清单、示例代码和典型错误案例；",
        "项目评分量规、答辩要求、参考项目和拓展学习资料。",
    ]:
        add_bullet(doc, text)
    doc.add_heading("（二）推荐资料", level=2)
    for text in [
        "MDN Web Docs：HTML、CSS、JavaScript和Web API参考；",
        "Vue 3、Vue Router、Pinia、Vite官方文档；",
        "Git、Axios、TypeScript、Vitest官方文档；",
        "学校选定的HTML5、CSS3、JavaScript ES6+或Vue 3项目化教材。",
    ]:
        add_bullet(doc, text)
    add_body(doc, "教材和网络教程不应成为唯一教学依据。课程应优先培养学生阅读官方文档、验证示例和辨别技术信息时效性的能力。正式备案时，应补充学校指定教材的作者、书名、出版社、版次和出版年份。")

    # 17 ideology
    doc.add_heading("十七、课程思政与职业素养融入", level=1)
    ideology_rows = [
        ("工程责任", "错误处理、数据校验和项目交付", "认识软件质量对真实用户的影响"),
        ("用户关怀", "响应式、可访问性和状态反馈", "形成以用户为中心的设计意识"),
        ("网络安全", "XSS风险、密钥和敏感信息管理", "树立安全开发和数据保护意识"),
        ("诚信规范", "代码引用、开源许可证和AI使用声明", "尊重知识产权，坚持学术诚信"),
        ("团队精神", "分支协作、代码审查和任务分工", "形成合作意识和责任意识"),
        ("精益求精", "调试、测试和性能检查", "培养严谨细致的工程作风"),
        ("自主创新", "拓展任务和方案比较", "培养自主探索和技术判断能力"),
        ("社会责任", "校园服务类项目", "理解软件技术服务学习与社会生活的价值"),
    ]
    add_table(doc, ["融入主题", "教学载体", "培养目标"], ideology_rows, widths=[3.0, 6.0, 7.0], font_size=9, center_cols=[0])

    # 18 AI
    doc.add_heading("十八、生成式人工智能使用规范", level=1)
    doc.add_heading("（一）允许的辅助方式", level=2)
    for text in [
        "解释错误信息，提供调试方向或测试思路；",
        "生成不含个人敏感信息的测试数据；",
        "比较技术方案，辅助完善注释、测试清单和项目文档；",
        "对学生已经完成的代码提出改进建议。",
    ]:
        add_bullet(doc, text)
    doc.add_heading("（二）必须遵守的要求", level=2)
    for text in [
        "学生能够解释、运行和修改本人提交的代码，并对正确性和安全性负责；",
        "在项目报告中说明所用工具、使用环节和人工核验方式；",
        "对生成内容进行自主测试，不直接采纳未经验证的答案；",
        "不得向外部工具提交真实密钥、个人信息、未公开代码或课程内部敏感数据。",
    ]:
        add_bullet(doc, text)
    doc.add_heading("（三）禁止行为", level=2)
    for text in [
        "直接生成整个项目并作为个人独立成果提交；",
        "无法解释本人提交的核心代码或使用AI代替本人答辩；",
        "伪造Git开发过程、测试记录或个人贡献证据；",
        "违反开源许可证、知识产权或学校学术诚信规定。",
    ]:
        add_bullet(doc, text)

    # 19 quality
    doc.add_heading("十九、教学质量保障与持续改进", level=1)
    quality_rows = [
        ("课前诊断", "检查HTML结构、CSS布局、数组处理、DOM事件、异步请求和Git基础；为基础薄弱学生提供预备材料"),
        ("每课验收", "设置最小可验收成果，通过运行、代码检查和学生解释进行快速评价"),
        ("阶段评审", "建议在第4、8、12、16次课分别检查页面、组件化、应用集成和最终交付"),
        ("学习预警", "连续两次未提交、项目长期无法运行、Git记录异常、无法解释代码或分工严重失衡时及时干预"),
        ("反馈改进", "统计目标达成度、任务完成率、高频错误、答辩问题和学生反馈，调整难度、范围、节奏和评分量规"),
    ]
    add_table(doc, ["环节", "实施要求"], quality_rows, widths=[3.2, 12.8], font_size=9.5, center_cols=[0])

    # 20 deliverables
    doc.add_heading("二十、学生最终提交清单", level=1)
    deliverables = [
        "完整项目源代码和Git仓库地址；",
        "可访问的在线部署地址；",
        "项目README和需求功能清单；",
        "页面、组件、路由、状态和接口结构说明；",
        "测试清单与缺陷修复记录；",
        "团队分工与个人贡献说明；",
        "项目总结报告和答辩材料；",
        "生成式人工智能使用声明。",
    ]
    for item in deliverables:
        add_numbered(doc, item)
    add_body(doc, "README至少包含项目简介、技术栈、主要功能、安装与运行命令、构建方法、目录结构、环境变量说明、项目截图、成员分工和已知问题。")

    # 21 completion
    doc.add_heading("二十一、课程完成标准", level=1)
    for text in [
        "独立或协作完成一个可运行的中小型前端项目；",
        "完成不少于80%的规定实践任务；",
        "能够使用Vue 3完成基本组件开发，并解释主要数据流；",
        "能够调用接口并处理常见请求状态；",
        "能够使用Git管理项目，完成生产构建和基本部署；",
        "能够解释本人负责的主要代码和缺陷修复过程；",
        "综合成绩达到60分及以上，并满足个人实践与诚信要求。",
    ]:
        add_bullet(doc, text)
    add_body(doc, "课程结束时，学生形成从“需求理解—方案设计—编码实现—接口联调—调试测试—协作交付—复盘改进”的完整软件工程实践闭环，为后续Web应用开发、综合实训和毕业设计奠定基础。")

    # Approval
    doc.add_heading("二十二、大纲审核信息", level=1)
    approval_rows = [
        ("编制人", "", "编制日期", "2026年7月"),
        ("课程负责人审核", "", "审核日期", ""),
        ("系（教研室）审核", "", "审核日期", ""),
        ("学院审核", "", "审核日期", ""),
    ]
    approval = add_table(doc, ["项目", "签字", "项目", "日期"], approval_rows, widths=[3.4, 4.6, 3.4, 4.6], font_size=10, center_cols=[0, 2])
    for row in approval.rows:
        row.height = Cm(1.0)

    # Update fields when opened in Word.
    settings = doc.settings._element
    update_fields = settings.find(qn("w:updateFields"))
    if update_fields is None:
        update_fields = OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set(qn("w:val"), "true")

    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(create_document())
