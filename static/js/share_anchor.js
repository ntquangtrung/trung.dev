function(editor) {
    function extractAnchorsFromContentEditor() {
        const content = tinymce.get('content-editor').getContent();

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;

        const anchors = [];
        tempDiv.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id], a[id]').forEach(el => {
            anchors.push({
                title: el.id,
                value: `#${el.id}`
            });
        });

        return anchors;
    }
    
    

    editor.on('init', function () {
        editor.options.set('link_list', function(success) {
            const dynamicAnchors = extractAnchorsFromContentEditor();
            success(dynamicAnchors);
        });
    });

    editor.on('focus', function () {
        editor.options.set('link_list', function(success) {
            const dynamicAnchors = extractAnchorsFromContentEditor();
            success(dynamicAnchors);
        });
    });
}
