package com.goodzheng.po.controller;

import com.goodzheng.po.shared.dto.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * 通用文件上传：供 App 端成品照、菜谱配图等非头像场景使用。
 * 文件落在 uploads/files/<dir>/，由静态资源映射以 /api/files/<dir>/<文件名> 访问。
 * 登录即可上传（归属权由业务侧记录）；目录白名单防止任意路径写入。
 */
@RestController
@RequestMapping("/files")
@RequiredArgsConstructor
public class FileController {

    /** 允许上传的图片类型及对应扩展名 */
    private static final Map<String, String> ALLOWED_IMAGE_TYPES = Map.of(
            "image/jpeg", "jpg",
            "image/png", "png",
            "image/gif", "gif",
            "image/webp", "webp");

    /** 允许的业务子目录（文件落在 uploads/files/<dir>/） */
    private static final Set<String> ALLOWED_DIRS = Set.of("common", "dishes", "steps");

    /** 单文件大小上限：10MB（与 spring.servlet.multipart.max-file-size 一致） */
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;

    // ── 通用图片上传（任何已登录用户） ──────────────────
    @PostMapping("/upload")
    public Result<String> upload(
            @RequestParam("file") MultipartFile file,
            @RequestParam(defaultValue = "common") String dir) {
        try {
            if (file == null || file.isEmpty()) {
                throw new RuntimeException("请选择要上传的文件");
            }
            if (!ALLOWED_DIRS.contains(dir)) {
                throw new RuntimeException("非法的上传目录: " + dir);
            }
            String contentType = file.getContentType();
            if (contentType == null || !ALLOWED_IMAGE_TYPES.containsKey(contentType)) {
                throw new RuntimeException("仅支持 jpg/png/gif/webp 格式的图片");
            }
            if (file.getSize() > MAX_FILE_SIZE) {
                throw new RuntimeException("文件不能超过 10MB");
            }
            String filename = UUID.randomUUID().toString().replace("-", "")
                    + "." + ALLOWED_IMAGE_TYPES.get(contentType);
            Path targetDir = Paths.get("uploads", "files", dir);
            try (InputStream in = file.getInputStream()) {
                Files.createDirectories(targetDir);
                Files.copy(in, targetDir.resolve(filename), StandardCopyOption.REPLACE_EXISTING);
            } catch (IOException e) {
                throw new RuntimeException("文件保存失败: " + e.getMessage());
            }
            return Result.success("上传成功", "/api/files/" + dir + "/" + filename);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }
}
