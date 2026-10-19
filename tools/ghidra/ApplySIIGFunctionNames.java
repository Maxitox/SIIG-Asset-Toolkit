// Applies conservative, evidence-based names to key Space Invaders Infinity Gene functions.
// @category Space Invaders Infinity Gene

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class ApplySIIGFunctionNames extends GhidraScript {
    private static class Rename {
        final String address;
        final String name;
        final String comment;
        Rename(String address, String name, String comment) {
            this.address = address;
            this.name = name;
            this.comment = comment;
        }
    }

    @Override
    public void run() throws Exception {
        Rename[] renames = new Rename[] {
            new Rename("82472568", "BBX_GetResourceCount",
                "Returns big-endian BBX header field +0x04 (resource count)."),
            new Rename("82472578", "BBX_GetDataByIndex",
                "Returns base + entry[index].data_offset. Entries start at +0x20 and are 0x10 bytes."),
            new Rename("824725B0", "BBX_GetSizeByIndex",
                "Returns entry[index].data_size from BBX entry +0x04."),
            new Rename("82472638", "BBX_GetNameByIndex",
                "Returns base + entry[index].name_offset, or null for unnamed entries."),
            new Rename("82472678", "BBX_GetDataByName",
                "Hashes a name, resolves the BBX entry, and returns the payload pointer."),
            new Rename("824726F0", "BBX_GetSizeByName",
                "Hashes a name, resolves the BBX entry, and returns the payload size."),
            new Rename("824739D0", "BBX_HashName",
                "Game-specific filename hash. Seed comes from BBX header +0x0C."),

            new Rename("821A0688", "LoadBBXArchiveAndRegisterResources",
                "Opens a .bin.gz/.bin.gz.sdat archive, enumerates name/data/size, and registers each resource."),
            new Rename("820E19A0", "ResourceTable_FindByName",
                "Linear strcmp over 0x88-byte ResourceEntry records."),
            new Rename("820E2A18", "ResourceTable_RegisterCopy",
                "Creates/updates ResourceEntry{name[0x80], data@+0x80, size@+0x84}."),
            new Rename("820E2828", "ResourceTable_GetDataAndSize",
                "Normalizes .png to .tex, then returns ResourceEntry data and optional size."),

            new Rename("824703C0", "GzipData_Inflate",
                "Inflates a gzip stream; nearby error strings explicitly name GzipData::Inflate()."),
            new Rename("8246D1D0", "TEX_LoadFromMemory",
                "Copies a 0x34-byte texture header and raw Xbox 360 texture payload, then creates the texture."),

            new Rename("82476188", "GMX_CountChunks",
                "Walks GMX chunks by their big-endian size and counts known four-character tags."),
            new Rename("82476498", "GMX_ParseChunks",
                "Allocates arrays for chunk classes and parses the GMX chunk stream."),
            new Rename("82477B60", "GMX_BuildRuntimeScene",
                "Builds runtime objects from parsed GMX BONE/MTRL/MESH/ARRY/etc. chunks."),
            new Rename("824785C0", "GMX_MeshRuntime_Init",
                "Initializes a runtime mesh wrapper and maps GMX/OpenGL primitive modes."),
            new Rename("8214B570", "GMX_Load",
                "Allocates a GMX object and loads from a provided memory pointer or wrapped buffer."),
        };

        int applied = 0;
        for (Rename item : renames) {
            if (monitor.isCancelled()) break;
            Address address = toAddr(item.address);
            Function function = currentProgram.getFunctionManager().getFunctionAt(address);
            if (function == null) {
                println("No function at " + item.address + " (skipped)");
                continue;
            }
            try {
                function.setName(item.name, SourceType.USER_DEFINED);
                currentProgram.getListing().setPlateComment(address, item.comment);
                println(item.address + " -> " + item.name);
                applied++;
            } catch (Exception ex) {
                printerr("Could not rename " + item.address + ": " + ex.getMessage());
            }
        }
        popup("Applied " + applied + " SIIG function names/comments.");
    }
}
