"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";

import { TextureButton } from "@/components/shared/TextureButton";
import { DESIGN_ASSETS, FINAL_ASSETS } from "@/lib/design/content";
import { getFontFamilyLabel } from "@/lib/formatters/display";
import type { EditableTextLayer, StaticDemoCharacter } from "@/lib/demo/static-demo-data";

interface FabricEditorShellProps {
  demo: StaticDemoCharacter;
}

type FabricModule = typeof import("fabric");
type CanvasObject = import("fabric").FabricObject;

interface EditorLayerItem {
  id: string;
  label: string;
  type: string;
}

const EDITOR_DEFAULT_FONT_FAMILY = "KaiTi, STKaiti, serif";
const EDITOR_DEFAULT_TEXT_FILL = "#2e241a";
const SYSTEM_FONT_FAMILIES = [EDITOR_DEFAULT_FONT_FAMILY, "Microsoft YaHei", "SimSun", "SimHei", "KaiTi", "FangSong", "serif", "sans-serif"] as const;

export function FabricEditorShell({ demo }: FabricEditorShellProps) {
  const canvasElementRef = useRef<HTMLCanvasElement | null>(null);
  const canvasShellRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<import("fabric").Canvas | null>(null);
  const resizeHandlerRef = useRef<(() => void) | null>(null);
  const fabricModuleRef = useRef<FabricModule | null>(null);
  const [ready, setReady] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedTextColor, setSelectedTextColor] = useState(EDITOR_DEFAULT_TEXT_FILL);
  const [selectedFontSize, setSelectedFontSize] = useState(48);
  const [selectedFontFamily, setSelectedFontFamily] = useState<(typeof SYSTEM_FONT_FAMILIES)[number]>(EDITOR_DEFAULT_FONT_FAMILY);
  const [selectedFontWeight, setSelectedFontWeight] = useState<"normal" | "bold">("normal");
  const [layers, setLayers] = useState<EditorLayerItem[]>([]);
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
  const [backgroundOpacity, setBackgroundOpacity] = useState(1);
  const [exportMessage, setExportMessage] = useState("");

  useEffect(() => {
    let disposed = false;

    async function initializeEditor() {
      if (!canvasElementRef.current) {
        return;
      }

      try {
        const fabricModule = await import("fabric");
        if (disposed) {
          return;
        }

        fabricModuleRef.current = fabricModule;

        const canvas = new fabricModule.Canvas(canvasElementRef.current, {
          width: demo.canvasWidth,
          height: demo.canvasHeight,
          backgroundColor: "#ffffff",
        });
        canvasRef.current = canvas;

        await applyBackgroundImage(canvas, fabricModule, demo.editorBackgroundImageUrl, demo.canvasWidth, demo.canvasHeight);
        addEditableTextLayers(canvas, fabricModule, demo.editableTextLayers);
        bindCanvasEvents(canvas);
        refreshLayers(canvas);
        fitCanvasToShell(canvas);
        resizeHandlerRef.current = () => fitCanvasToShell(canvas);
        window.addEventListener("resize", resizeHandlerRef.current);
        setReady(true);
      } catch (error) {
        const message = error instanceof Error ? error.message : "编辑器初始化失败。";
        setErrorMessage(message);
      }
    }

    initializeEditor();

    return () => {
      disposed = true;
      if (resizeHandlerRef.current) {
        window.removeEventListener("resize", resizeHandlerRef.current);
        resizeHandlerRef.current = null;
      }
      canvasRef.current?.dispose();
      canvasRef.current = null;
    };
  }, [demo.canvasHeight, demo.canvasWidth, demo.editorBackgroundImageUrl, demo.editableTextLayers]);

  function bindCanvasEvents(canvas: import("fabric").Canvas) {
    const events = ["object:added", "object:modified", "object:removed"] as const;
    events.forEach((eventName) => {
      canvas.on(eventName, () => {
        syncSelectedStyles();
        refreshLayers(canvas);
      });
    });

    canvas.on("selection:created", syncSelectedStyles);
    canvas.on("selection:updated", syncSelectedStyles);
    canvas.on("selection:cleared", syncSelectedStyles);
  }

  function fitCanvasToShell(canvas: import("fabric").Canvas) {
    const shell = canvasShellRef.current;
    if (!shell) {
      return;
    }

    const availableWidth = Math.max(320, shell.clientWidth - 32);
    const scale = Math.min(1, availableWidth / demo.canvasWidth);
    canvas.setDimensions(
      {
        width: Math.round(demo.canvasWidth * scale),
        height: Math.round(demo.canvasHeight * scale),
      },
      { cssOnly: true },
    );
    canvas.requestRenderAll();
  }

  function syncSelectedStyles() {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const activeObject = canvas.getActiveObject();
    if (!activeObject || !isTextObject(activeObject)) {
      setSelectedFontSize(48);
      setSelectedTextColor(EDITOR_DEFAULT_TEXT_FILL);
      setSelectedLayerId(activeObject ? getObjectId(activeObject) : null);
      return;
    }

    const fontSize = typeof activeObject.get("fontSize") === "number" ? Number(activeObject.get("fontSize")) : 48;
    const fill = typeof activeObject.get("fill") === "string" ? String(activeObject.get("fill")) : EDITOR_DEFAULT_TEXT_FILL;
    const fontFamily = typeof activeObject.get("fontFamily") === "string" ? String(activeObject.get("fontFamily")) : EDITOR_DEFAULT_FONT_FAMILY;
    const fontWeight = activeObject.get("fontWeight") === "bold" ? "bold" : "normal";
    setSelectedFontSize(fontSize);
    setSelectedTextColor(fill);
    setSelectedFontFamily(SYSTEM_FONT_FAMILIES.includes(fontFamily as (typeof SYSTEM_FONT_FAMILIES)[number]) ? (fontFamily as (typeof SYSTEM_FONT_FAMILIES)[number]) : EDITOR_DEFAULT_FONT_FAMILY);
    setSelectedFontWeight(fontWeight);
    setSelectedLayerId(getObjectId(activeObject));
  }

  function addEditableTextLayers(
    canvas: import("fabric").Canvas,
    fabricModule: FabricModule,
    editableTextLayers: EditableTextLayer[],
  ) {
    editableTextLayers.forEach((layer) => {
      canvas.add(createTextboxFromLayer(fabricModule, layer, demo.canvasWidth, demo.canvasHeight));
    });
    canvas.requestRenderAll();
  }

  function createTextboxFromLayer(
    fabricModule: FabricModule,
    layer: EditableTextLayer,
    canvasWidth: number,
    canvasHeight: number,
  ) {
    const [x, y, width, height] = layer.boxNorm;
    const textbox = new fabricModule.Textbox(layer.text, {
      left: x * canvasWidth,
      top: (1 - y - height) * canvasHeight,
      width: width * canvasWidth,
      height: height * canvasHeight,
      fill: layer.fill ?? EDITOR_DEFAULT_TEXT_FILL,
      fontSize: layer.fontSize9 * canvasHeight / 9,
      fontFamily: EDITOR_DEFAULT_FONT_FAMILY,
      fontWeight: layer.fontWeight ?? "normal",
      textAlign: layer.textAlign,
      lineHeight: layer.lineHeight,
      editable: true,
      selectable: true,
      evented: true,
      splitByGrapheme: true,
      transparentCorners: false,
    });
    textbox.set("id", layer.id);
    textbox.set("data", { role: "editable-text", label: layer.label });
    return textbox;
  }

  async function applyBackgroundImage(
    canvas: import("fabric").Canvas,
    fabricModule: FabricModule,
    backgroundImageUrl: string,
    width: number,
    height: number,
  ) {
    const image = await fabricModule.FabricImage.fromURL(backgroundImageUrl, { crossOrigin: "anonymous" });
    image.set({
      left: 0,
      top: 0,
      opacity: backgroundOpacity,
      selectable: false,
      evented: false,
      data: { role: "background" },
    });
    image.scaleToWidth(width);
    image.scaleToHeight(height);
    canvas.add(image);
    canvas.sendObjectToBack(image);
    canvas.requestRenderAll();
  }

  function handleAddText() {
    const canvas = canvasRef.current;
    const fabricModule = fabricModuleRef.current;
    if (!canvas || !fabricModule) {
      return;
    }

    const text = new fabricModule.Textbox("请输入注释", {
      left: 140,
      top: 160,
      width: Math.min(420, demo.canvasWidth / 3),
      fill: selectedTextColor,
      fontSize: selectedFontSize,
      fontFamily: selectedFontFamily,
      fontWeight: selectedFontWeight,
      editable: true,
    });
    text.set("id", `note-${Date.now()}`);
    text.set("data", { role: "note", label: "新增注释" });
    canvas.add(text);
    canvas.setActiveObject(text);
    canvas.requestRenderAll();
  }

  function handleDeleteSelected() {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const activeObject = canvas.getActiveObject();
    if (!activeObject) {
      return;
    }

    canvas.remove(activeObject);
    canvas.discardActiveObject();
    canvas.requestRenderAll();
  }

  function handleFontSizeChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFontSize = Number(event.target.value);
    setSelectedFontSize(nextFontSize);

    const canvas = canvasRef.current;
    const activeObject = canvas?.getActiveObject();
    if (!canvas || !activeObject || !isTextObject(activeObject)) {
      return;
    }

    activeObject.set("fontSize", nextFontSize);
    canvas.requestRenderAll();
  }

  function handleFontFamilyChange(event: ChangeEvent<HTMLSelectElement>) {
    const nextFontFamily = event.target.value as (typeof SYSTEM_FONT_FAMILIES)[number];
    setSelectedFontFamily(nextFontFamily);

    const canvas = canvasRef.current;
    const activeObject = canvas?.getActiveObject();
    if (!canvas || !activeObject || !isTextObject(activeObject)) {
      return;
    }

    activeObject.set("fontFamily", nextFontFamily);
    canvas.requestRenderAll();
  }

  function handleTextColorChange(event: ChangeEvent<HTMLInputElement>) {
    const nextColor = event.target.value;
    setSelectedTextColor(nextColor);

    const canvas = canvasRef.current;
    const activeObject = canvas?.getActiveObject();
    if (!canvas || !activeObject || !isTextObject(activeObject)) {
      return;
    }

    activeObject.set("fill", nextColor);
    canvas.requestRenderAll();
  }

  function handleToggleFontWeight() {
    const nextFontWeight = selectedFontWeight === "bold" ? "normal" : "bold";
    setSelectedFontWeight(nextFontWeight);

    const canvas = canvasRef.current;
    const activeObject = canvas?.getActiveObject();
    if (!canvas || !activeObject || !isTextObject(activeObject)) {
      return;
    }

    activeObject.set("fontWeight", nextFontWeight);
    canvas.requestRenderAll();
  }

  function handleExportPng() {
    const canvas = canvasRef.current;
    if (!canvas) {
      setExportMessage("画布尚未加载完成，请稍后再试。");
      return;
    }

    try {
      const dataUrl = canvas.toDataURL({
        format: "png",
        multiplier: 1,
      });
      const link = document.createElement("a");
      link.href = dataUrl;
      link.download = `wensheng-demo-${demo.character}.png`;
      link.click();
      setExportMessage("PNG 已开始导出。");
    } catch (error) {
      const message = error instanceof Error ? error.message : "导出失败，请保留当前画布截图。";
      setExportMessage(`导出失败：${message}`);
    }
  }

  function handleSelectLayer(layerId: string) {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const target = canvas.getObjects().find((object) => getObjectId(object) === layerId);
    if (!target) {
      return;
    }

    canvas.setActiveObject(target);
    setSelectedLayerId(layerId);
    syncSelectedStyles();
    canvas.requestRenderAll();
  }

  function handleBackgroundOpacityChange(event: ChangeEvent<HTMLInputElement>) {
    const nextOpacity = Number(event.target.value);
    setBackgroundOpacity(nextOpacity);

    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const background = canvas.getObjects().find((object) => (object.get("data") as { role?: string } | undefined)?.role === "background");
    background?.set("opacity", nextOpacity);
    canvas.requestRenderAll();
  }

  function refreshLayers(canvas = canvasRef.current) {
    if (!canvas) {
      return;
    }

    const nextLayers = canvas
      .getObjects()
      .filter((object) => (object.get("data") as { role?: string } | undefined)?.role !== "background")
      .map((object, index) => {
        const data = object.get("data") as { label?: string } | undefined;
        return {
          id: getObjectId(object) ?? `layer-${index}`,
          label: data?.label ?? (isTextObject(object) ? "文本图层" : "形状图层"),
          type: object.type,
        };
      })
      .reverse();
    setLayers(nextLayers);
  }

  function getObjectId(object: CanvasObject) {
    const id = object.get("id");
    return typeof id === "string" ? id : null;
  }

  function isTextObject(object: CanvasObject) {
    return object.type === "i-text" || object.type === "textbox" || object.type === "text";
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
      <section
        className="overflow-hidden rounded-[8px] shadow-[0_16px_36px_rgba(45,28,12,0.14)]"
        style={{
          backgroundImage: `linear-gradient(rgba(230,210,170,0.94), rgba(230,210,170,0.94)), url(${DESIGN_ASSETS.cardBackground})`,
          backgroundPosition: "center",
          backgroundSize: "cover",
        }}
      >
        <div className="p-6">
          <h2 className="font-[var(--font-display)] text-[24px] text-[#4c2e18]">微调工具</h2>
          <p className="mt-2 text-[14px] leading-6 text-[#6b5336]">
            当前为静态演示项目。画布以“{demo.character}”的固定文化解析图为底图，可添加少量注释并导出。
          </p>
          <div className="mt-6 space-y-4">
            <button className="editor-toolbar-button px-4 py-3" onClick={handleAddText} type="button">
              添加注释层
            </button>
            <div className="rounded-[8px] border border-[rgba(107,66,38,0.14)] bg-[rgba(255,248,236,0.66)] p-4">
              <h3 className="text-[14px] font-medium text-[#4c2e18]">图层</h3>
              <div className="mt-3 max-h-[260px] space-y-2 overflow-auto">
                {layers.length ? (
                  layers.map((layer) => (
                    <button
                      key={layer.id}
                      className={`w-full rounded-[8px] border px-3 py-2 text-left text-[13px] ${
                        selectedLayerId === layer.id
                          ? "border-[rgba(107,66,38,0.52)] bg-[rgba(255,248,236,0.94)] text-[#3f2615]"
                          : "border-[rgba(107,66,38,0.14)] bg-[rgba(255,248,236,0.52)] text-[#6b5336]"
                      }`}
                      onClick={() => handleSelectLayer(layer.id)}
                      type="button"
                    >
                      <span className="block font-medium">{layer.label}</span>
                      <span className="mt-1 block text-[12px] opacity-75">{layer.type}</span>
                    </button>
                  ))
                ) : (
                  <p className="text-[13px] leading-6 text-[#6b5336]">暂无注释图层。</p>
                )}
              </div>
            </div>
            <label className="block rounded-[8px] border border-[rgba(107,66,38,0.14)] bg-[rgba(255,248,236,0.66)] p-4 text-[14px] font-medium text-[#4c2e18]">
              背景透明度
              <input className="mt-3 w-full" max="1" min="0.35" onChange={handleBackgroundOpacityChange} step="0.05" type="range" value={backgroundOpacity} />
              <span className="mt-1 block text-[13px] text-[#6b5336]">{Math.round(backgroundOpacity * 100)}%</span>
            </label>
            <div className="rounded-[8px] border border-[rgba(107,66,38,0.14)] bg-[rgba(255,248,236,0.66)] p-4">
              <h3 className="text-[14px] font-medium text-[#4c2e18]">文字设置</h3>
              <div className="mt-4 space-y-4">
                <label className="block text-[14px] font-medium text-[#4c2e18]">
                  字体
                  <select
                    className="mt-2 w-full rounded-[8px] border border-[rgba(107,66,38,0.18)] bg-[rgba(255,248,236,0.88)] px-3 py-2 text-[14px] text-[#4c2e18]"
                    onChange={handleFontFamilyChange}
                    value={selectedFontFamily}
                  >
                    {SYSTEM_FONT_FAMILIES.map((fontFamily) => (
                      <option key={fontFamily} value={fontFamily}>
                        {getFontFamilyLabel(fontFamily)}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block text-[14px] font-medium text-[#4c2e18]">
                  字号
                  <input className="mt-2 w-full" max="160" min="12" onChange={handleFontSizeChange} type="range" value={selectedFontSize} />
                  <span className="mt-1 block text-[14px] text-[#6b5336]">{selectedFontSize}px</span>
                </label>
                <label className="block text-[14px] font-medium text-[#4c2e18]">
                  文字颜色
                  <input
                    className="mt-2 h-10 w-full rounded-[8px] border border-[rgba(107,66,38,0.18)]"
                    onChange={handleTextColorChange}
                    type="color"
                    value={selectedTextColor}
                  />
                </label>
                <div className="space-y-2">
                  <span className="block text-[14px] font-medium text-[#4c2e18]">字重</span>
                  <button
                    className={`editor-toolbar-button px-4 py-3 ${selectedFontWeight === "bold" ? "editor-toolbar-button--active" : ""}`}
                    onClick={handleToggleFontWeight}
                    type="button"
                  >
                    {selectedFontWeight === "bold" ? "当前：加粗" : "当前：常规"}
                  </button>
                </div>
              </div>
            </div>
            <button className="editor-toolbar-button px-4 py-3" onClick={handleDeleteSelected} type="button">
              删除选中元素
            </button>
            <TextureButton
              backgroundImage={DESIGN_ASSETS.buttonBackground}
              className="mx-auto"
              onClick={handleExportPng}
              type="button"
            >
              导出 PNG
            </TextureButton>
            {exportMessage ? <p className="text-[13px] leading-6 text-[#6b5336]">{exportMessage}</p> : null}
          </div>
        </div>
      </section>

      <section className="ornate-panel p-6">
        <h2 className="font-[var(--font-display)] text-[24px] text-[#4c2e18]">最终效果图画布</h2>
        {errorMessage ? <p className="mt-4 text-[14px] text-[#b42318]">{errorMessage}</p> : null}
        {!ready ? <p className="mt-4 text-[14px] text-[#6b5336]">编辑器加载中...</p> : null}
        <div
          ref={canvasShellRef}
          className="final-art-canvas-frame mt-4 overflow-auto rounded-[8px] border border-[rgba(107,66,38,0.18)] bg-[rgba(255,248,236,0.54)] bg-cover bg-center p-4"
          style={{ backgroundImage: `linear-gradient(rgba(255,248,236,0.66), rgba(255,248,236,0.66)), url(${FINAL_ASSETS.editorWorkspaceBackground})` }}
        >
          <canvas ref={canvasElementRef} />
        </div>
      </section>
    </div>
  );
}
