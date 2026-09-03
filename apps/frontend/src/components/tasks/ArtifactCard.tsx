import { Download, FileText } from "lucide-react";
import type { Artifact } from "../../types";

export function ArtifactCard({ artifact }: { artifact: Artifact }) { return <div className="artifact-card"><div className="artifact-icon"><FileText size={20} /></div><div><strong>{artifact.name}</strong><span>{artifact.type}{artifact.size ? ` · ${artifact.size}` : ""}</span></div>{artifact.downloadUrl ? <a className="download-button" href={artifact.downloadUrl} download={artifact.name}><Download size={16} /> Download</a> : <button className="download-button unavailable-download" disabled title="Artifact download is not available until the backend result endpoint is connected"><Download size={16} /> Awaiting file</button>}</div>; }
