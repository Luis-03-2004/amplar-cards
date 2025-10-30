import { useState, type ChangeEvent } from 'react'

type UploadState = 'idle' | 'uploading' | 'success' | 'error'
export function FileUploader() {
    const [templatesLandscape, setTemplatesLandscape] = useState<File[]>([])
    const [templatesPortrait, setTemplatesPortrait] = useState<File[]>([])
    const [images, setImages] = useState<File[]>([])
    const [zipFile, setZipFile] = useState<File | null>(null)
    const [state, setState] = useState<UploadState>('idle')
    const [progress, setProgress] = useState<number>(0)
    const [isProcessing, setIsProcessing] = useState<boolean>(false)
    const [downloadUrl, setDownloadUrl] = useState<string | null>(null)

    function FileButton({ id, label, accept, multiple, onChange }: { id: string, label: string, accept: string, multiple?: boolean, onChange: (e: ChangeEvent<HTMLInputElement>) => void }) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <label htmlFor={id} style={{
                    background: '#16a34a',
                    color: '#fff',
                    padding: '8px 14px',
                    borderRadius: 9999,
                    cursor: 'pointer',
                    fontSize: 14,
                    fontWeight: 600,
                    display: 'inline-block'
                }}> {label} </label>
                <input id={id} type="file" accept={accept} multiple={multiple} onChange={onChange} style={{ display: 'none' }} />
            </div>
        )
    }

    function handleTemplatesLandscape(e: ChangeEvent<HTMLInputElement>) {
        setTemplatesLandscape(e.target.files ? Array.from(e.target.files) : [])
    }
    function handleTemplatesPortrait(e: ChangeEvent<HTMLInputElement>) {
        setTemplatesPortrait(e.target.files ? Array.from(e.target.files) : [])
    }
    function handleImages(e: ChangeEvent<HTMLInputElement>) {
        setImages(e.target.files ? Array.from(e.target.files) : [])
    }
    function handleZip(e: ChangeEvent<HTMLInputElement>) {
        setZipFile(e.target.files && e.target.files[0] ? e.target.files[0] : null)
    }

    async function handleFileUpload(){
        // needs at least one template
        if (templatesLandscape.length === 0 && templatesPortrait.length === 0) return
        setState('uploading');
        setProgress(0)
        setDownloadUrl(null)
        setIsProcessing(false)

        const formData = new FormData();
        for (const f of templatesLandscape) formData.append('templates_landscape', f)
        for (const f of templatesPortrait) formData.append('templates_portrait', f)
        if (zipFile) {
            formData.append('images_zip', zipFile)
        } else {
            for (const f of images) formData.append('images', f)
        }

        try {
            const xhr = new XMLHttpRequest()
            xhr.open('POST', 'http://localhost:5000/images/process')
            xhr.responseType = 'blob'
            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    setProgress(Math.round((e.loaded / e.total) * 100))
                }
            }
            // When the upload is finished, we show the processing phase
            xhr.upload.onload = () => {
                setIsProcessing(true)
            }
            const done: Blob = await new Promise((resolve, reject) => {
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) resolve(xhr.response)
                    else reject(new Error(`HTTP ${xhr.status}`))
                }
                xhr.onerror = () => reject(new Error('Network error'))
                xhr.send(formData)
            })
            setState('success')
            // Link to download the ZIP
            const url = URL.createObjectURL(done)
            setDownloadUrl(url)
        }catch(error){
            console.error('Erro ao fazer upload:', error);
            setState('error');
        }finally{
            setIsProcessing(false)
        }
    }

    return(
        <div className='space-y-2' style={{ width: '100%' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, alignItems: 'start' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <FileButton id="tl" label="Selecionar Templates Landscape" accept="image/png" multiple onChange={handleTemplatesLandscape} />
                    <small style={{ color: '#555' }}>{templatesLandscape.length > 0 ? `${templatesLandscape.length} arquivo(s) selecionado(s)` : 'Nenhum template landscape selecionado'}</small>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <FileButton id="tp" label="Selecionar Templates Portrait" accept="image/png" multiple onChange={handleTemplatesPortrait} />
                    <small style={{ color: '#555' }}>{templatesPortrait.length > 0 ? `${templatesPortrait.length} arquivo(s) selecionado(s)` : 'Nenhum template portrait selecionado'}</small>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <FileButton id="imgs" label="Selecionar Fotos (JPG/PNG)" accept="image/jpeg,image/png" multiple onChange={handleImages} />
                    <small style={{ color: '#555' }}>{images.length > 0 ? `${images.length} foto(s) selecionada(s)` : 'Nenhuma foto selecionada'}</small>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <FileButton id="zip" label="Selecionar ZIP de Fotos" accept="application/zip" onChange={handleZip} />
                    <small style={{ color: '#555' }}>{zipFile ? zipFile.name : 'Nenhum ZIP selecionado'}</small>
                </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 24, alignItems: 'center', flexWrap: 'wrap' }}>
                {(images.length > 0 || zipFile || templatesLandscape.length > 0 || templatesPortrait.length > 0) && state !== 'uploading' && (
                    <button onClick={handleFileUpload} style={{
                        background: '#2563eb', color: '#fff', padding: '10px 18px', borderRadius: 9999, border: 'none', cursor: 'pointer', fontWeight: 600
                    }}>Processar</button>
                )}

                {state === 'uploading' && !isProcessing && (
                    <div style={{ minWidth: 220 }}>
                        <div style={{ height: 8, background: '#eee', borderRadius: 4 }}>
                            <div style={{ width: `${progress}%`, height: '100%', background: '#3b82f6', borderRadius: 4 }} />
                        </div>
                        <div style={{ fontSize: 12, marginTop: 4, textAlign: 'center' }}>{progress}%</div>
                    </div>
                )}
                {state === 'uploading' && isProcessing && (
                    <div className="mt-2 text-sm" style={{ textAlign: 'center' }}>Processando imagens no servidor...</div>
                )}

                {downloadUrl && (
                    <button onClick={() => {
                        if (!downloadUrl) return
                        const a = document.createElement('a')
                        a.href = downloadUrl
                        a.download = 'processed_images.zip'
                        document.body.appendChild(a)
                        a.click()
                        a.remove()
                    }} style={{
                        background: '#059669', color: '#fff', padding: '10px 18px', borderRadius: 9999, border: 'none', cursor: 'pointer', fontWeight: 600
                    }}>Baixar ZIP</button>
                )}
            </div>

            <div style={{ textAlign: 'center', marginTop: 8 }}>
                {state === 'success' && (
                    <span className="text-sm" style={{ color: '#16a34a' }}>Arquivos convertidos com sucesso.</span>
                )}
                {state === 'error' && (
                    <span className="text-sm" style={{ color: '#dc2626' }}>Erro ao fazer upload</span>
                )}
            </div>
        </div>
    )
}