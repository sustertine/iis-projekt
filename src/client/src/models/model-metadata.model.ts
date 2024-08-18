export interface ModelMetadata {
    model_name: string;
    version: string;
    run_id: string;
    start_time: number;
    end_time: number;
    status: string;
    params: any;
}